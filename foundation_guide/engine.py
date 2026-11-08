"""The game engine: parser dispatch, world state, saves, and meta commands."""

from __future__ import annotations

import copy
import difflib
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from . import guide
from .episodes import EPISODE_COUNT, load_episode
from .model import NPC, Exit, Object, Room, World
from .parser import VERBS, Command, parse
from .state import ActState, Meta
from .ui import UI, join_names

def _default_save_dir() -> Path:
    """Keep saves beside a source checkout, and in user data when installed."""
    override = os.environ.get("FOUNDATION_GUIDE_SAVE_DIR")
    if override:
        return Path(override).expanduser()

    project_root = Path(__file__).resolve().parent.parent
    if (project_root / "pyproject.toml").is_file():
        return project_root / "saves"

    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "foundation-guide" / "saves"


SAVE_DIR = _default_save_dir()
SAVE_FORMAT = "foundation-guide"
SAVE_VERSION = 1
CORE_GUIDE = {"THE GUIDE", "DON'T PANIC", "TOWEL"}
META_VERBS = {
    "help",
    "about",
    "version",
    "score",
    "inventory",
    "guide",
    "hint",
    "map",
    "save",
    "load",
    "restart",
    "undo",
    "verbose",
    "brief",
    "status",
    "achievements",
    "quit",
}
STOPWORDS = {
    "the",
    "a",
    "an",
    "some",
    "my",
    "your",
    "his",
    "her",
    "their",
    "this",
    "that",
    "these",
    "those",
    "of",
    "to",
    "in",
    "on",
    "at",
}
ROMAN = {0: "I", 1: "II", 2: "III", 3: "IV"}


def _tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9']+", text.lower()) if t not in STOPWORDS}


def _norm(text: str) -> str:
    text = text.lower().replace("\u2019", "'")
    text = re.sub(r"[^a-z0-9' ]+", " ", text)
    return " ".join(text.split())


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def print_manual(ui: UI) -> None:
    ui.say()
    ui.say(ui.bold("THE GUIDE'S QUICK REFERENCE"))
    ui.say()
    ui.say(ui.cyan("MOVEMENT"))
    ui.say("  north/south/east/west/up/down (or n, s, e, w, u, d)")
    ui.say("  GO <exit>, ENTER <place>, EXIT, BOARD <ship>")
    ui.say()
    ui.say(ui.cyan("EXPLORATION"))
    ui.say("  LOOK, EXAMINE <thing>, READ <thing>, SEARCH <thing>")
    ui.say("  TAKE <thing>, TAKE ALL, DROP <thing>, INVENTORY")
    ui.say("  OPEN/CLOSE <thing>, UNLOCK <thing> WITH <key>")
    ui.say("  WEAR/REMOVE <thing>, PUT <thing> IN/ON <thing>")
    ui.say()
    ui.say(ui.cyan("PEOPLE AND PUZZLES"))
    ui.say("  TALK TO <person>, ASK <person> ABOUT <topic>")
    ui.say("  GIVE <thing> TO <person>, SHOW <thing> TO <person>")
    ui.say("  USE <thing> [ON <thing>], PUSH/PULL/PRESS/TURN/SWITCH <thing>")
    ui.say("  SET <thing> TO <value>, TYPE <text>, SAY <words>")
    ui.say()
    ui.say(ui.cyan("THE GUIDE"))
    ui.say("  GUIDE              list unlocked entries")
    ui.say("  GUIDE <topic>      read an entry")
    ui.say("  HINT               a contextual nudge (never costs points)")
    ui.say("  MAP                a map of the places you have visited")
    ui.say("  SCORE              your score, rank, and statistics")
    ui.say()
    ui.say(ui.cyan("HOUSEKEEPING"))
    ui.say("  SAVE [name]        save the game (default: quicksave)")
    ui.say("  LOAD [name]        load a save (default: quicksave)")
    ui.say("  UNDO               rewind one turn")
    ui.say("  RESTART            begin again (asks for confirmation)")
    ui.say("  QUIT               leave the simulation")
    ui.say()
    ui.say(ui.dim("The parser is forgiving: articles are optional, IT/THEM work,\n"
                  "and most verbs have sensible abbreviations. If you are stuck,\n"
                  "HINT is cheaper than despair. Death rewinds one turn; there are\n"
                  "no unwinnable states."))
    ui.say()
    ui.say(ui.dim("Autosaves are written at the start of each act. Manual saves live\n"
                  f"in {SAVE_DIR}."))
    ui.say()


class Game:
    def __init__(
        self,
        ui: UI,
        act_index: int = 0,
        meta: Meta | None = None,
        state: ActState | None = None,
        debug: bool = False,
    ) -> None:
        self.ui = ui
        self.debug = debug
        self.act_index = act_index
        self.world: World = load_episode(act_index)
        self.meta: Meta = meta or Meta(
            started_at=time.time(), guide_unlocked=set(CORE_GUIDE)
        )
        self.state: ActState = state or self._new_state()
        self.snapshots: list[ActState] = []
        self.running = True
        self._skip_after = False
        self._death = False
        self._end_handled = False
        self._ambiguous = False
        self.current_verb = ""
        self._first_help_hint = False

    # ------------------------------------------------------------------
    # Setup and flow
    # ------------------------------------------------------------------
    def _new_state(self) -> ActState:
        state = ActState(room=self.world.start_room, verbose=True)
        for key, obj in self.world.objects.items():
            state.obj_loc[key] = obj.location
            state.obj_open[key] = obj.open
            state.obj_locked[key] = obj.locked
        return state

    def start_new(self) -> None:
        self.meta = Meta(started_at=time.time(), guide_unlocked=set(CORE_GUIDE))
        self.act_index = 0
        self.world = load_episode(0)
        self.state = self._new_state()
        self.snapshots = []
        self.running = True
        self._end_handled = False
        self._skip_after = True
        self.start_act()

    def start_act(self) -> None:
        self.ui.act_header(
            f"Act {ROMAN.get(self.act_index, self.act_index + 1)}",
            self.world.title,
            self.world.subtitle,
            f"You are {self.world.protagonist}.",
        )
        self.ui.narrate(self._text(self.world.intro))
        new_entries: list[str] = []
        for key in self.world.guide_keys:
            if key not in self.meta.guide_unlocked and guide.exists(key):
                self.meta.guide_unlocked.add(key)
                new_entries.append(key)
        if new_entries:
            self.ui.say(
                self.ui.cyan("The Guide updates: " + ", ".join(new_entries) + ".")
            )
            self.ui.say()
        if self.world.on_start:
            self.world.on_start(self)
        self.enter_room(self.world.start_room, first=True)
        if self.act_index == 0 and not self._first_help_hint:
            self._first_help_hint = True
            self.ui.say(
                self.ui.dim(
                    "(Type HELP for commands, GUIDE for the Guide, HINT for a nudge.)"
                )
            )
            self.ui.say()

    def play(self) -> None:
        self.run()

    def run(self) -> None:
        while self.running:
            if self.state.finished:
                self.end_act()
                if not self.running:
                    break
                continue
            try:
                raw = self.ui.read_command()
            except EOFError:
                self.ui.say()
                self.ui.say(self.ui.dim("The Guide closes the book, leaving the story unfinished."))
                break
            except KeyboardInterrupt:
                self.ui.say()
                self.ui.say(self.ui.dim("The Guide pretends not to have noticed the interruption."))
                break
            self.execute(raw)

    def execute(self, raw: str) -> None:
        if not raw or not raw.strip():
            return

        # Confirmation prompts are handled before the parser.
        if self.state.pending == "restart":
            answer = raw.strip().lower()
            self.state.pending = None
            if answer in ("yes", "y"):
                self.ui.say("The Guide rewinds to the beginning. It is sorry about the mess.")
                self.start_new()
            else:
                self.ui.say("The Guide puts the scissors away. Your journey continues.")
            return

        self._skip_after = False
        self._death = False
        self.snapshots.append(copy.deepcopy(self.state))
        if len(self.snapshots) > 40:
            self.snapshots.pop(0)

        cmd = parse(raw)
        if cmd is None:
            return
        self.current_verb = cmd.verb
        if cmd.verb not in META_VERBS:
            self.state.moves += 1

        try:
            self.dispatch(cmd)
        except Exception as exc:  # pragma: no cover - defensive at runtime
            if self.debug:
                raise
            if self.snapshots:
                self.state = self.snapshots.pop()
            self.ui.error(
                "The Guide encounters a narrative singularity and hastily reverses time."
            )
            self.ui.say(self.ui.dim(f"({type(exc).__name__}: {exc})"))
            return

        if self._death or self._skip_after:
            return
        if not self.state.finished:
            self.after_turn()

    def after_turn(self) -> None:
        if self.world.on_turn:
            self.world.on_turn(self)

    def finish_act(self) -> None:
        self.state.finished = True
        self._skip_after = True

    def teleport(self, room_key: str, first: bool | None = None) -> None:
        self.enter_room(room_key, first=first)

    def end_act(self) -> None:
        if self._end_handled:
            return
        self._end_handled = True
        self.meta.act_scores[self.act_index] = self.state.score
        self.ui.say()
        self.ui.rule("=")
        self.ui.say(
            self.ui.bold(
                f"ACT {ROMAN.get(self.act_index, self.act_index + 1)} COMPLETE"
            )
        )
        self.ui.say(
            f"Act score: {self.state.score}/{self.world.max_score}    "
            f"Total: {self.total_score()}/{EPISODE_COUNT * 100}"
        )
        self.ui.say(
            f"Rank: {self.rank_for(self.state.score, self.world.max_score, final=False)}"
        )
        self.ui.say(
            self.ui.dim(
                f"Moves: {self.state.moves}    Deaths: {self.meta.deaths}    "
                f"Hints: {self.meta.hints}    Guide entries: {len(self.meta.guide_unlocked)}"
            )
        )
        self.ui.rule("=")
        if self.act_index + 1 < EPISODE_COUNT:
            self.ui.say()
            self.ui.say(self.ui.italic("The Guide turns the page. Somewhere, a century passes."))
            self.ui.pause("Press ENTER to travel forward in time...")
            self.advance_act()
            return

        # Final act.
        self.ui.say()
        if self.world.epilogue:
            self.ui.narrate(self._text(self.world.epilogue))
        self.ui.say(self.ui.bold(self.world.ending_title))
        self.ui.say(
            self.ui.bold(
                f"Final score: {self.total_score()}/{EPISODE_COUNT * 100} — "
                f"{self.rank_for(self.total_score(), EPISODE_COUNT * 100, final=True)}"
            )
        )
        self.ui.say(
            self.ui.dim(
                f"Deaths: {self.meta.deaths}    Hints: {self.meta.hints}    "
                f"Guide entries: {len(self.meta.guide_unlocked)}/{len(guide.ENTRIES)}"
            )
        )
        if self.meta.achievements:
            self.ui.say(self.ui.dim("Achievements: " + ", ".join(sorted(self.meta.achievements))))
        self.ui.say()
        self.ui.say(self.ui.cyan("So long, and thanks for all the psychohistory."))
        self.ui.say()
        self.running = False

    def advance_act(self) -> None:
        self.act_index += 1
        if self.act_index >= EPISODE_COUNT:
            self.running = False
            return
        self.world = load_episode(self.act_index)
        self.state = self._new_state()
        self.snapshots = []
        self._end_handled = False
        self._skip_after = True
        self.start_act()
        self.save("autosave", quiet=True)

    def new_game(self) -> None:
        self.meta = Meta(started_at=time.time(), guide_unlocked=set(CORE_GUIDE))
        self.act_index = 0
        self.world = load_episode(0)
        self.state = self._new_state()
        self.snapshots = []
        self.running = True
        self._end_handled = False
        self._skip_after = True
        self.start_act()

    # ------------------------------------------------------------------
    # Text and score helpers
    # ------------------------------------------------------------------
    def _text(self, value: Any) -> str:
        if callable(value):
            result = value(self)
            return "" if result is None else str(result)
        return "" if value is None else str(value)

    def say(self, text: object = "") -> None:
        self.ui.say(text)

    def narrate(self, text: object = "") -> None:
        self.ui.narrate(text)

    def has(self, flag: str) -> bool:
        return flag in self.state.flags

    def set_flag(self, flag: str) -> None:
        self.state.flags.add(flag)

    def clear_flag(self, flag: str) -> None:
        self.state.flags.discard(flag)

    def counter(self, key: str) -> int:
        return self.state.counters.get(key, 0)

    def inc_counter(self, key: str, amount: int = 1) -> int:
        self.state.counters[key] = self.state.counters.get(key, 0) + amount
        return self.state.counters[key]

    def total_score(self) -> int:
        completed = sum(
            value for key, value in self.meta.act_scores.items() if key != self.act_index
        )
        return completed + self.state.score

    def award(self, points: int, reason: str = "") -> None:
        if points <= 0:
            return
        remaining = max(0, self.world.max_score - self.state.score)
        actual = min(points, remaining)
        if actual <= 0:
            return
        self.state.score += actual
        message = f"[+{actual} points]"
        if reason:
            message += f" {reason}"
        self.ui.award(message)
        if self.state.score >= self.world.max_score and "max_score_announced" not in self.state.flags:
            self.state.flags.add("max_score_announced")
            self.ui.say(
                self.ui.dim("You have reached the maximum score for this act. The Guide is quietly impressed.")
            )

    def award_once(self, tag: str, points: int, reason: str = "") -> None:
        flag = "awarded:" + tag
        if flag in self.state.flags:
            return
        self.state.flags.add(flag)
        self.award(points, reason)

    def unlock_guide(self, key: str, quiet: bool = False) -> bool:
        if not guide.exists(key):
            if self.debug:
                self.ui.warning(f"(The Guide has no entry named {key!r}.)")
            return False
        if key in self.meta.guide_unlocked:
            return False
        self.meta.guide_unlocked.add(key)
        if not quiet:
            self.ui.say(self.ui.cyan(f"The Guide updates: {key}."))
        return True

    def achievement(self, name: str, quiet: bool = False) -> None:
        if name in self.meta.achievements:
            return
        self.meta.achievements.add(name)
        if not quiet:
            self.ui.say(self.ui.dim(f"Achievement: {name}."))

    def rank_for(self, score: int, maximum: int, final: bool = False) -> str:
        pct = score / maximum if maximum else 0
        if final:
            if pct >= 0.99:
                return "The Second Foundation's Favourite Probability"
            if pct >= 0.86:
                return "Mayor of Terminus"
            if pct >= 0.66:
                return "Trained Psychohistorian"
            if pct >= 0.50:
                return "Useful Idiot of History"
            if pct >= 0.33:
                return "Hitchhiker, Second Class"
            return "Mostly Harmless"
        if pct >= 0.99:
            return "The Guide's Favourite Probability"
        if pct >= 0.85:
            return "Psychohistorical Overachiever"
        if pct >= 0.70:
            return "Raven Seldon's Understudy"
        if pct >= 0.50:
            return "Competent Bystander"
        if pct >= 0.30:
            return "Assistant Deputy Filing Clerk"
        return "Mostly Harmless"

    def death(self, message: str = "") -> None:
        if self._death:
            return
        self._death = True
        self.meta.deaths += 1
        self.ui.say()
        self.ui.error(message or "You have died. The Galaxy barely notices.")
        if self.snapshots:
            self.state = self.snapshots.pop()
            self.ui.say(
                self.ui.dim(
                    "The Guide sighs, reverses time by one turn, and pretends this never happened."
                )
            )
            self.ui.say(
                self.ui.dim(
                    f"You are back in {self.world.rooms[self.state.room].name}. "
                    "Try a different probability."
                )
            )
        else:
            self.ui.say(
                self.ui.dim("The Guide cannot rewind. It improvises by putting you back at the start.")
            )
            self.state = self._new_state()
            self.enter_room(self.world.start_room, first=True)
        self._skip_after = True

    die = death

    # ------------------------------------------------------------------
    # Objects, NPCs, rooms
    # ------------------------------------------------------------------
    def room(self) -> Room:
        return self.world.rooms[self.state.room]

    def obj(self, key: str) -> Object:
        return self.world.objects[key]

    def npc(self, key: str) -> NPC:
        return self.world.npcs[key]

    def obj_name(self, key: str, article: bool = False) -> str:
        obj = self.world.objects[key]
        name = obj.display_name()
        if article and not name.lower().startswith(("the ", "a ", "an ")):
            return "the " + name
        return name

    def is_carried(self, key: str) -> bool:
        loc = self.state.obj_loc.get(key)
        if loc == "player" or key in self.state.obj_worn:
            return True
        if loc in self.world.objects:
            container = self.world.objects[loc]
            open_now = self.state.obj_open.get(loc, container.open)
            return self.is_carried(loc) and (open_now or container.transparent)
        return False

    def is_visible_obj(self, key: str, _seen: set[str] | None = None) -> bool:
        loc = self.state.obj_loc.get(key)
        if loc is None:
            return False
        if loc == self.state.room:
            return True
        if loc == "player" or key in self.state.obj_worn:
            return True
        if loc in self.world.objects:
            if _seen is None:
                _seen = set()
            if loc in _seen:
                return False
            _seen.add(loc)
            container = self.world.objects[loc]
            if not self.is_visible_obj(loc, _seen):
                return False
            return bool(self.state.obj_open.get(loc, container.open)) or container.transparent
        return False

    def contents(self, key: str) -> list[str]:
        return [
            other_key
            for other_key, obj in self.world.objects.items()
            if self.state.obj_loc.get(other_key) == key and not obj.hidden
        ]

    def _contents_phrase(self, key: str) -> str:
        keys = sorted(self.contents(key), key=lambda k: self.obj_name(k))
        if not keys:
            return ""
        return join_names(self.obj_name(k, article=True) for k in keys)

    def _match_score(self, names: list[str], query: str) -> int:
        q = _norm(query)
        if not q:
            return 0
        qt = _tokens(q)
        best = 0
        for raw_name in names:
            name = _norm(raw_name)
            if not name:
                continue
            if q == name:
                return 1000 + len(name)
            nt = _tokens(name)
            if qt and qt <= nt:
                best = max(best, 600 + len(nt))
            elif q in name:
                best = max(best, 350 + len(q))
            elif name in q:
                best = max(best, 200 + len(name))
            else:
                common = len(qt & nt)
                if common:
                    best = max(best, int(100 * common / max(1, len(qt))))
                ratio = difflib.SequenceMatcher(None, q, name).ratio()
                if ratio >= 0.78:
                    best = max(best, int(120 * ratio))
        return best

    def _object_names(self, obj: Object) -> list[str]:
        return list(dict.fromkeys([obj.display_name(), *obj.names, obj.key.replace("_", " ")]))

    def _candidate_objects(self, scope: str = "visible", container: str | None = None) -> list[str]:
        keys: list[str] = []
        for key, obj in self.world.objects.items():
            if obj.hidden:
                continue
            loc = self.state.obj_loc.get(key)
            if scope == "visible":
                if self.is_visible_obj(key):
                    keys.append(key)
            elif scope == "inventory":
                if self.is_carried(key):
                    keys.append(key)
            elif scope == "room":
                if loc == self.state.room:
                    keys.append(key)
            elif scope == "container":
                if container and loc == container:
                    keys.append(key)
            elif scope == "all":
                if loc is not None:
                    keys.append(key)
        return keys

    def _sort_key(self, key: str, score: int) -> tuple[int, int, int]:
        loc = self.state.obj_loc.get(key)
        if loc == "player" or key in self.state.obj_worn:
            priority = 3
        elif loc == self.state.room:
            priority = 2
        else:
            priority = 1
        return (score, priority, -len(key))

    def resolve_object(self, query: str | None, scope: str = "visible") -> Object | None:
        self._ambiguous = False
        if not query:
            return None
        query = query.strip()
        if query.lower() in ("it", "them"):
            key = self.state.pronoun
            if key and key in self.world.objects and self.is_visible_obj(key):
                return self.world.objects[key]
            self.ui.say("The Guide has lost track of what 'it' refers to. It blames the pronoun industry.")
            return None
        candidates = self._candidate_objects(scope)
        scored: list[tuple[int, str]] = []
        for key in candidates:
            obj = self.world.objects[key]
            score = self._match_score(self._object_names(obj), query)
            if score > 0:
                scored.append((score, key))
        if not scored:
            return None
        scored.sort(key=lambda item: self._sort_key(item[1], item[0]), reverse=True)
        best_score = scored[0][0]
        top = [key for score, key in scored if score == best_score]
        if len(top) > 1:
            # If two objects share the exact same display name (two towels),
            # ask which one.  Otherwise prefer the first by location priority.
            names = {self.obj_name(key) for key in top}
            if len(names) == 1:
                self.state.pronoun = top[0]
                return self.world.objects[top[0]]
            if best_score < 900:
                self._ambiguous = True
                self.ui.say("Which do you mean: " + join_names(self.obj_name(key) for key in top) + "?")
                return None
        return self.world.objects[scored[0][1]]

    def resolve_npc(self, query: str | None) -> NPC | None:
        if not query:
            return None
        query = query.strip()
        if query.lower() in ("it", "them"):
            key = self.state.pronoun
            if key and key in self.world.npcs:
                return self.world.npcs[key]
            return None
        candidates = [
            key
            for key, npc in self.world.npcs.items()
            if npc.location == self.state.room and npc.listed
        ]
        scored: list[tuple[int, str]] = []
        for key in candidates:
            npc = self.world.npcs[key]
            names = list(dict.fromkeys([npc.display_name(), *npc.names, key.replace("_", " ")]))
            score = self._match_score(names, query)
            if score:
                scored.append((score, key))
        if not scored:
            return None
        scored.sort(key=lambda item: item[0], reverse=True)
        best_score = scored[0][0]
        top = [key for score, key in scored if score == best_score]
        if len(top) > 1 and best_score < 900:
            self.ui.say(
                "Which one do you mean: "
                + join_names(self.world.npcs[key].display_name() for key in top)
                + "?"
            )
            return None
        return self.world.npcs[scored[0][1]]

    def resolve_any(self, query: str | None) -> Object | NPC | None:
        if not query:
            return None
        # An exact name match on a person beats a loose substring match on an
        # object.  "MIS" should reach Ebling Mis, not his notes.
        q = _norm(query)
        exact_npcs = [
            key
            for key, npc in self.world.npcs.items()
            if npc.location == self.state.room
            and npc.listed
            and any(
                _norm(name) == q
                for name in [npc.display_name(), *npc.names, key.replace("_", " ")]
            )
        ]
        if len(exact_npcs) == 1:
            return self.world.npcs[exact_npcs[0]]
        obj = self.resolve_object(query, "visible")
        if obj is not None:
            return obj
        if self._ambiguous:
            return None
        return self.resolve_npc(query)

    def find_extra(self, query: str) -> str | None:
        room = self.room()
        q = _norm(query)
        if not q:
            return None
        qt = _tokens(q)
        best: tuple[int, str] | None = None
        for key, text in room.extras.items():
            k = _norm(key)
            kt = _tokens(k)
            score = 0
            if q == k:
                score = 100
            elif q in k or k in q:
                score = 60
            elif qt and qt <= kt:
                score = 50
            if score and (best is None or score > best[0]):
                best = (score, text)
        return best[1] if best else None

    def no_object(self, query: str | None) -> None:
        if query and query.strip().lower() in ("guide", "the guide"):
            self.do_guide(None)
            return
        if not query:
            self.ui.say("You examine the air. It is unusually translucent.")
            return
        visible = [
            self.obj_name(key)
            for key in self._candidate_objects("visible")
        ]
        visible += [
            npc.display_name()
            for npc in self.world.npcs.values()
            if npc.location == self.state.room and npc.listed
        ]
        suggestions = difflib.get_close_matches(query, visible, n=3, cutoff=0.55)
        text = f"You can't see any {query} here."
        if suggestions:
            text += " The Guide wonders whether you mean " + join_names(suggestions) + "."
        self.ui.say(text)

    def _with_article(self, name: str) -> str:
        if name.lower().startswith(("the ", "a ", "an ")):
            return name
        return "the " + name

    def describe_room(self, first: bool = False) -> None:
        room = self.room()
        if room.dark and "light" not in self.state.flags:
            self.ui.say(self.ui.bold(self.ui.cyan(room.name)))
            self.ui.say("It is pitch dark. You can hear your own probabilities.")
            self.ui.say()
            self.status_line()
            return

        self.ui.say(self.ui.bold(self.ui.cyan(room.name)))
        if first or self.state.verbose or room.brief is None:
            self.ui.say(self._text(room.desc))
        else:
            self.ui.say(self._text(room.brief))
        self.ui.say()

        objects = sorted(
            [
                key
                for key, obj in self.world.objects.items()
                if self.state.obj_loc.get(key) == self.state.room and obj.listed and not obj.hidden
            ],
            key=lambda key: self.obj_name(key),
        )
        npcs = sorted(
            [
                npc
                for npc in self.world.npcs.values()
                if npc.location == self.state.room and npc.listed
            ],
            key=lambda npc: npc.display_name(),
        )
        if objects:
            self.ui.say(
                "You see " + join_names(self._with_article(self.obj_name(key)) for key in objects) + "."
            )
        if npcs:
            self.ui.say("Also here: " + join_names(self._with_article(npc.display_name()) for npc in npcs) + ".")
        self.ui.say()

        exits = [exit.label or key for key, exit in room.exits.items() if not exit.hidden]
        if exits:
            self.ui.say("Exits: " + ", ".join(exits) + ".")
        else:
            self.ui.say("There is no obvious way out. The Guide suggests examining your assumptions.")
        self.ui.say()
        self.status_line()

    def status_line(self) -> None:
        room = self.room()
        self.ui.status(
            f"Act {ROMAN.get(self.act_index, self.act_index + 1)} | {room.name} | "
            f"Score {self.state.score}/{self.world.max_score} | "
            f"Total {self.total_score()}/{EPISODE_COUNT * 100} | Turn {self.state.moves}"
        )

    def enter_room(self, dest: str, first: bool | None = None) -> None:
        if dest not in self.world.rooms:
            self.ui.error("The Guide has misplaced that room. This is embarrassing.")
            return
        if first is None:
            first = dest not in self.state.seen
        self.state.room = dest
        self.state.seen.add(dest)
        self.state.pronoun = None
        if self.world.on_enter:
            self.world.on_enter(self, dest)
        self.describe_room(first)
        room = self.room()
        if first and room.on_enter:
            room.on_enter(self, True)

    def find_exit(self, room: Room, direction: str) -> tuple[str, Exit] | None:
        direction = _norm(direction)
        if direction in ("n", "s", "e", "w", "ne", "nw", "se", "sw", "u", "d"):
            direction = {
                "n": "north", "s": "south", "e": "east", "w": "west",
                "ne": "northeast", "nw": "northwest", "se": "southeast",
                "sw": "southwest", "u": "up", "d": "down",
            }[direction]
        for key, exit in room.exits.items():
            candidates = {_norm(key)}
            if exit.label:
                candidates.add(_norm(exit.label))
            dest_room = self.world.rooms.get(exit.dest)
            if dest_room:
                candidates.add(_norm(dest_room.name))
                candidates.add(_norm(dest_room.key))
            if direction in candidates:
                return key, exit
        # A forgiving fallback for custom exit names (e.g. "service lift").
        for key, exit in room.exits.items():
            if direction and (_norm(key).startswith(direction) or direction.startswith(_norm(key))):
                return key, exit
        return None

    def do_go(self, direction: str) -> None:
        if not direction:
            self.ui.say("Go where? The Guide suggests a direction, or at least a confident gesture.")
            return
        direction = direction.strip()
        room = self.room()
        found = self.find_exit(room, direction)
        if not found:
            self.ui.say(f"There is no way {direction} from here. The Guide checked twice.")
            return
        _, exit = found
        if exit.on_use:
            result = exit.on_use(self)
            if result:
                return
        if exit.condition and not exit.condition(self):
            self.ui.say(exit.blocked)
            return
        self.enter_room(exit.dest)

    def do_look(self, target: str | None = None) -> None:
        if target:
            self.do_examine(target)
            return
        self.describe_room(False)

    def do_examine(self, target: str | None) -> None:
        if not target:
            self.do_look(None)
            return
        low = target.strip().lower()
        if low in ("guide", "the guide", "book"):
            self.do_guide(None)
            return
        if low in ("me", "myself", "self"):
            self.ui.say(f"You are {self.world.protagonist}.")
            self.ui.say(
                "You appear to be a person of reasonable intelligence and unreasonable optimism. "
                "The Guide approves."
            )
            return
        if low in ("room", "here", "around"):
            self.describe_room(False)
            return
        obj = self.resolve_object(target, "visible")
        if obj:
            self.state.pronoun = obj.key
            self.ui.say(self._text(obj.desc))
            if obj.container:
                if self.state.obj_open.get(obj.key, obj.open) or obj.transparent:
                    phrase = self._contents_phrase(obj.key)
                    if phrase:
                        self.ui.say(f"It contains {phrase}.")
                    else:
                        self.ui.say("It is empty, apart from the usual existential residue.")
                else:
                    self.ui.say("It is closed.")
            if obj.locked:
                self.ui.say("It is locked.")
            if obj.wearable and obj.key in self.state.obj_worn:
                self.ui.say("You are wearing it.")
            if obj.readable:
                self.ui.say(self.ui.dim("(You could READ it.)"))
            return
        npc = self.resolve_npc(target)
        if npc:
            self.state.pronoun = npc.key
            self.ui.say(self._text(npc.desc))
            if npc.topics:
                topics = sorted(npc.topics.keys())
                preview = ", ".join(topics[:5])
                if len(topics) > 5:
                    preview += ", and others"
                self.ui.say(self.ui.dim(f"You could ASK them ABOUT: {preview}."))
            return
        extra = self.find_extra(target)
        if extra:
            self.ui.say(extra)
            return
        self.no_object(target)

    def do_read(self, target: str | None) -> None:
        if not target:
            self.ui.say("Read what? The Guide suggests GUIDE, which is also a hint.")
            return
        if target.strip().lower() in ("guide", "the guide", "book"):
            self.do_guide(None)
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            extra = self.find_extra(target)
            if extra:
                self.ui.say(extra)
            else:
                self.no_object(target)
            return
        self.state.pronoun = obj.key
        if obj.on_read:
            if obj.on_read(self, obj):
                return
        if obj.readable is None:
            self.ui.say(f"There is no writing on the {obj.display_name()} that the Guide is willing to translate.")
            return
        self.ui.say(self._text(obj.readable))

    def do_search(self, target: str | None) -> None:
        if not target:
            self.ui.say("You search the room with the thoroughness of a tax auditor.")
            for key, text in self.room().extras.items():
                if key in ("sound", "smell"):
                    continue
                self.ui.say(text)
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            extra = self.find_extra(target)
            if extra:
                self.ui.say(extra)
            else:
                self.no_object(target)
            return
        self.state.pronoun = obj.key
        if obj.on_search:
            if obj.on_search(self, obj):
                return
        if obj.container:
            if not (self.state.obj_open.get(obj.key, obj.open) or obj.transparent):
                self.ui.say(f"You would have to open the {obj.display_name()} first.")
                return
            phrase = self._contents_phrase(obj.key)
            if phrase:
                self.ui.say(f"You find {phrase}.")
            else:
                self.ui.say("You find nothing but dust and the faint smell of a disappointed archivist.")
            return
        self.ui.say(self._text(obj.desc))
        self.ui.say("You find nothing you did not already suspect.")

    def do_open(self, target: str | None) -> None:
        if not target:
            self.ui.say("Open what? The Guide has a list of suggestions, all of them doors.")
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            self.no_object(target)
            return
        self.state.pronoun = obj.key
        if not (obj.container or obj.openable):
            self.ui.say("That is not the sort of thing that opens. It barely closes.")
            return
        if self.state.obj_open.get(obj.key, obj.open):
            self.ui.say(f"The {obj.display_name()} is already open.")
            return
        if self.state.obj_locked.get(obj.key, obj.locked):
            key_obj = self.world.objects.get(obj.unlock_key) if obj.unlock_key else None
            if key_obj and self.is_carried(key_obj.key):
                self.state.obj_locked[obj.key] = False
                self.ui.say(
                    f"You unlock the {obj.display_name()} with the {key_obj.display_name()}."
                )
            else:
                self.ui.say(f"The {obj.display_name()} is locked.")
                if key_obj:
                    self.ui.say(f"The {key_obj.display_name()} might help.")
                return
        self.state.obj_open[obj.key] = True
        if obj.on_open:
            if obj.on_open(self, obj):
                return
        self.ui.say(f"You open the {obj.display_name()}.")
        if obj.container:
            phrase = self._contents_phrase(obj.key)
            if phrase:
                self.ui.say(f"It contains {phrase}.")

    def do_close(self, target: str | None) -> None:
        if not target:
            self.ui.say("Close what?")
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            self.no_object(target)
            return
        if not (obj.container or obj.openable):
            self.ui.say("That does not close, which is either a relief or a design flaw.")
            return
        if not self.state.obj_open.get(obj.key, obj.open):
            self.ui.say(f"The {obj.display_name()} is already closed.")
            return
        if obj.on_close:
            if obj.on_close(self, obj):
                return
        self.state.obj_open[obj.key] = False
        self.ui.say(f"You close the {obj.display_name()}.")

    def do_unlock(self, target: str | None, key_name: str | None = None) -> None:
        if not target:
            self.ui.say("Unlock what?")
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            self.no_object(target)
            return
        if not self.state.obj_locked.get(obj.key, obj.locked):
            self.ui.say(f"The {obj.display_name()} is not locked.")
            return
        key_obj = self.resolve_object(key_name, "inventory") if key_name else None
        if key_obj is None and obj.unlock_key:
            candidate = self.world.objects.get(obj.unlock_key)
            if candidate and self.is_carried(candidate.key):
                key_obj = candidate
        if key_obj is None:
            self.ui.say("You do not have the right key. The Guide checks its pockets.")
            return
        if obj.unlock_key and key_obj.key != obj.unlock_key:
            self.ui.say(f"The {key_obj.display_name()} does not fit. It is not even the right shape of key.")
            return
        self.state.obj_locked[obj.key] = False
        self.ui.say(f"You unlock the {obj.display_name()} with the {key_obj.display_name()}.")

    def do_lock(self, target: str | None, key_name: str | None = None) -> None:
        if not target:
            self.ui.say("Lock what?")
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            self.no_object(target)
            return
        if self.state.obj_open.get(obj.key, obj.open):
            self.ui.say(f"You would have to close the {obj.display_name()} first.")
            return
        key_obj = self.resolve_object(key_name, "inventory") if key_name else None
        if key_obj is None and obj.unlock_key:
            candidate = self.world.objects.get(obj.unlock_key)
            if candidate and self.is_carried(candidate.key):
                key_obj = candidate
        if key_obj is None:
            self.ui.say("You do not have the right key.")
            return
        if obj.unlock_key and key_obj.key != obj.unlock_key:
            self.ui.say(f"The {key_obj.display_name()} does not fit.")
            return
        self.state.obj_locked[obj.key] = True
        self.ui.say(f"You lock the {obj.display_name()}.")

    def do_take(self, target: str | None) -> None:
        if not target:
            self.ui.say("Take what? The Guide suggests the towel, but the Guide always suggests the towel.")
            return
        if target.strip().lower() in ("all", "everything"):
            self.do_take_all()
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            self.no_object(target)
            return
        self._take_one(obj)

    def _take_one(self, obj: Object) -> None:
        loc = self.state.obj_loc.get(obj.key)
        if loc == "player" or obj.key in self.state.obj_worn:
            self.ui.say(f"You are already carrying the {obj.display_name()}.")
            return
        if loc in self.world.objects:
            container = self.world.objects[loc]
            if not (self.state.obj_open.get(loc, container.open) or container.transparent):
                self.ui.say(f"You would have to open the {container.display_name()} first.")
                return
        if obj.fixed or not obj.takeable:
            self.ui.say(f"The {obj.display_name()} is fixed in place. The Guide approves of stable scenery.")
            return
        if obj.on_take:
            if obj.on_take(self, obj):
                return
        self.state.obj_loc[obj.key] = "player"
        self.state.pronoun = obj.key
        self.ui.say(f"You take the {obj.display_name()}.")

    def do_take_all(self) -> None:
        keys = [
            key
            for key, obj in self.world.objects.items()
            if self.state.obj_loc.get(key) == self.state.room and obj.listed and not obj.hidden
        ]
        if not keys:
            self.ui.say("There is nothing here worth taking. The Guide admires your restraint.")
            return
        took = False
        for key in sorted(keys, key=lambda k: self.obj_name(k)):
            obj = self.world.objects[key]
            if not obj.takeable or obj.fixed:
                continue
            took = True
            self._take_one(obj)
        if not took:
            self.ui.say("Everything here is either fixed, alive, or emotionally unavailable.")

    def do_drop(self, target: str | None) -> None:
        if not target:
            self.ui.say("Drop what?")
            return
        obj = self.resolve_object(target, "inventory")
        if not obj:
            self.ui.say("You are not carrying that. The Guide checks under the sofa anyway.")
            return
        if obj.on_drop:
            if obj.on_drop(self, obj):
                return
        if obj.key in self.state.obj_worn:
            self.state.obj_worn.discard(obj.key)
        self.state.obj_loc[obj.key] = self.state.room
        self.state.pronoun = obj.key
        self.ui.say(f"You drop the {obj.display_name()}.")

    def do_put(self, target: str | None, preposition: str | None, container_name: str | None) -> None:
        if not target or not container_name:
            self.ui.say("Put what where? The Guide needs both halves of the sentence.")
            return
        obj = self.resolve_object(target, "inventory")
        if not obj:
            self.ui.say("You are not carrying that.")
            return
        recipient = self.resolve_any(container_name)
        if recipient is None:
            self.no_object(container_name)
            return
        if isinstance(recipient, NPC):
            self.ui.say("You can't put something in a person. Try GIVE.")
            return
        container = recipient
        if not (container.container or container.surface):
            self.ui.say(f"You can't put anything {'on' if preposition == 'on' else 'in'} the {container.display_name()}.")
            return
        if container.container and not self.state.obj_open.get(container.key, container.open):
            self.ui.say(f"You would have to open the {container.display_name()} first.")
            return
        if container.key == obj.key:
            self.ui.say("That is a topological impossibility, even by Imperial standards.")
            return
        # Avoid putting a container inside itself, directly or indirectly.
        loc = self.state.obj_loc.get(container.key)
        seen: set[str] = set()
        while loc in self.world.objects and loc not in seen:
            seen.add(loc)
            if loc == obj.key:
                self.ui.say("That would make the universe fold in on itself. The Guide is not insured for that.")
                return
            loc = self.state.obj_loc.get(loc)
        self.state.obj_loc[obj.key] = container.key
        self.state.pronoun = obj.key
        if container.on_receive:
            if container.on_receive(self, container, obj):
                return
        where = "on" if container.surface and preposition == "on" else "in"
        self.ui.say(f"You put the {obj.display_name()} {where} the {container.display_name()}.")

    def do_inventory(self) -> None:
        carried = [
            key
            for key, obj in self.world.objects.items()
            if self.state.obj_loc.get(key) == "player" and key not in self.state.obj_worn
        ]
        worn = sorted(self.state.obj_worn)
        if carried:
            self.ui.say("You are carrying: " + join_names(self.obj_name(key) for key in sorted(carried)) + ".")
        else:
            self.ui.say("You are carrying nothing but potential.")
        if worn:
            self.ui.say("You are wearing: " + join_names(self.obj_name(key) for key in worn) + ".")
        self.ui.say(self.ui.dim("The Guide is in your head, where it can keep an eye on you."))

    def do_wear(self, target: str | None) -> None:
        if not target:
            self.ui.say("Wear what?")
            return
        obj = self.resolve_object(target, "inventory")
        if not obj:
            self.ui.say("You are not carrying that.")
            return
        if not obj.wearable:
            self.ui.say(f"You can't wear the {obj.display_name()}. The Guide has standards, if not many.")
            return
        if obj.key in self.state.obj_worn:
            self.ui.say(f"You are already wearing the {obj.display_name()}.")
            return
        self.state.obj_worn.add(obj.key)
        self.ui.say(f"You put on the {obj.display_name()}.")

    def do_remove(self, target: str | None) -> None:
        if not target:
            self.ui.say("Remove what?")
            return
        obj = self.resolve_object(target, "inventory")
        if not obj:
            self.ui.say("You are not carrying that.")
            return
        if obj.key not in self.state.obj_worn:
            self.ui.say(f"You are not wearing the {obj.display_name()}.")
            return
        self.state.obj_worn.discard(obj.key)
        self.ui.say(f"You remove the {obj.display_name()}.")

    def do_give(self, target: str | None, npc_name: str | None) -> None:
        if not target or not npc_name:
            self.ui.say("Give what to whom? The Guide needs a full sentence, or at least a generous gesture.")
            return
        obj = self.resolve_object(target, "inventory")
        if not obj:
            self.ui.say("You are not carrying that.")
            return
        npc = self.resolve_npc(npc_name)
        if not npc:
            self.ui.say("There is no one here by that description. The Guide suggests lowering your expectations.")
            return
        if npc.on_give:
            if npc.on_give(self, npc, obj):
                return
        self.ui.say(f"The {npc.display_name()} politely declines the {obj.display_name()}.")

    def do_show(self, target: str | None, npc_name: str | None) -> None:
        if not target or not npc_name:
            self.ui.say("Show what to whom?")
            return
        obj = self.resolve_object(target, "inventory")
        if not obj:
            self.ui.say("You are not carrying that.")
            return
        npc = self.resolve_npc(npc_name)
        if not npc:
            self.ui.say("There is no one here by that description.")
            return
        if npc.on_show:
            if npc.on_show(self, npc, obj):
                return
        self.ui.say(f"The {npc.display_name()} glances at the {obj.display_name()} without visible interest.")

    def do_talk(self, target: str | None) -> None:
        if not target:
            npcs = [
                npc for npc in self.world.npcs.values()
                if npc.location == self.state.room and npc.listed
            ]
            if npcs:
                self.ui.say("You could talk to " + join_names(npc.display_name() for npc in npcs) + ".")
            else:
                self.ui.say("There is no one here to talk to. The Guide suggests talking to yourself, but it has heard you.")
            return
        npc = self.resolve_npc(target)
        if not npc:
            self.ui.say("There is no one here by that description.")
            return
        self.state.pronoun = npc.key
        self.state.flags.add(f"talked:{npc.key}")
        if npc.on_talk:
            if npc.on_talk(self, npc):
                return
        self.ui.say(self._text(npc.desc))
        if npc.topics:
            topics = sorted(npc.topics.keys())
            preview = ", ".join(topics[:5])
            if len(topics) > 5:
                preview += ", and others"
            self.ui.say(self.ui.dim(f"You could ASK them ABOUT: {preview}."))

    def _match_topic(self, npc: NPC, topic: str) -> str | None:
        q = _norm(topic)
        if not q:
            return None
        qt = _tokens(q)
        best: tuple[int, str] | None = None
        for key in npc.topics:
            k = _norm(key)
            kt = _tokens(k)
            score = 0
            if q == k:
                score = 100
            elif q in k or k in q:
                score = 75
            elif qt and kt and (qt <= kt or kt <= qt):
                score = 60
            elif qt and kt and qt & kt:
                score = 30 + 10 * len(qt & kt)
            if score and (best is None or score > best[0]):
                best = (score, key)
        return best[1] if best else None

    def do_ask(self, npc_name: str | None, topic: str | None) -> None:
        if not npc_name:
            self.ui.say("Ask whom?")
            return
        npc = self.resolve_npc(npc_name)
        if not npc:
            obj = self.resolve_object(npc_name, "visible")
            if obj:
                self.ui.say(f"The {obj.display_name()} is not much of a conversationalist.")
            else:
                self.ui.say("There is no one here by that description.")
            return
        self.state.pronoun = npc.key
        if not topic:
            topics = sorted(npc.topics.keys())
            if topics:
                self.ui.say("Ask about what? Possible topics: " + ", ".join(topics[:8]) + ".")
            else:
                self.ui.say(f"The {npc.display_name()} has nothing to say about anything.")
            return
        if npc.on_ask:
            if npc.on_ask(self, npc, topic):
                return
        key = self._match_topic(npc, topic)
        if not key:
            self.ui.say(self._text(npc.default))
            return
        self.state.flags.add(f"asked:{npc.key}:{_slug(key)}")
        value = npc.topics[key]
        if callable(value):
            result = value(self)
            if isinstance(result, str):
                self.ui.say(result)
            return
        self.ui.say(str(value))

    def do_say(self, text: str | None) -> None:
        if not text:
            self.ui.say("You say nothing. It is a start.")
            return
        text = text.strip()
        if self.world.on_say:
            result = self.world.on_say(self, text)
            if isinstance(result, str):
                self.ui.say(result)
                return
            if result:
                return
        for npc in self.world.npcs.values():
            if npc.location == self.state.room and npc.on_say:
                result = npc.on_say(self, npc, text)
                if isinstance(result, str):
                    self.ui.say(result)
                    return
                if result:
                    return
        ending = "" if text[-1:] in ".?!" else "."
        self.ui.say(f'You say, "{text}{ending}"')

    def do_type(self, text: str | None) -> None:
        if not text:
            self.ui.say("Type what?")
            return
        if self.world.on_type:
            result = self.world.on_type(self, text)
            if isinstance(result, str):
                self.ui.say(result)
                return
            if result:
                return
        self.ui.say(f'You type "{text}" into the nearest available surface. Nothing happens.')

    def do_use(self, target: str | None, indirect: str | None = None) -> None:
        if not target:
            self.ui.say("Use what?")
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            self.no_object(target)
            return
        if obj.takeable and not obj.fixed and not self.is_carried(obj.key):
            self.ui.say(f"You'll have to pick up the {obj.display_name()} first.")
            return
        target_obj: Object | NPC | None = None
        if indirect:
            target_obj = self.resolve_any(indirect)
            if target_obj is None:
                self.no_object(indirect)
                return
        self.state.pronoun = obj.key
        if obj.on_use:
            result = obj.on_use(self, obj, target_obj)
            if isinstance(result, str):
                self.ui.say(result)
                return
            if result:
                return
        if target_obj and obj.on_use_with:
            result = obj.on_use_with(self, obj, target_obj)
            if isinstance(result, str):
                self.ui.say(result)
                return
            if result:
                return
        if target_obj and isinstance(target_obj, Object) and target_obj.on_use_with:
            result = target_obj.on_use_with(self, target_obj, obj)
            if isinstance(result, str):
                self.ui.say(result)
                return
            if result:
                return
        if target_obj:
            self.ui.say(
                f"You try to use the {obj.display_name()} on the {getattr(target_obj, 'display_name', lambda: 'thing')()}. "
                "Nothing happens, except a small increase in embarrassment."
            )
        else:
            self.ui.say(
                f"You can't think of a way to use the {obj.display_name()}. "
                "The Guide suggests a towel. The Guide always suggests a towel."
            )

    def _manipulate(self, verb: str, target: str | None, value: str | None = None) -> None:
        if not target:
            self.ui.say(f"{verb.capitalize()} what?")
            return
        obj = self.resolve_object(target, "visible")
        if not obj:
            self.no_object(target)
            return
        self.state.pronoun = obj.key
        callback = None
        if verb == "push":
            callback = obj.on_push
        elif verb == "pull":
            callback = obj.on_pull
        elif verb == "press":
            callback = obj.on_press
        elif verb == "switch":
            callback = obj.on_switch
        elif verb == "switch_on":
            callback = obj.on_switch_on or obj.on_switch
        elif verb == "switch_off":
            callback = obj.on_switch_off or obj.on_switch
        elif verb == "turn":
            callback = obj.on_switch
        elif verb == "set":
            callback = obj.on_set
        if callback:
            try:
                result = callback(self, obj, value) if verb == "set" else callback(self, obj)
            except TypeError:
                result = callback(self, obj)
            if isinstance(result, str):
                self.ui.say(result)
                return
            if result:
                return
        if verb == "press":
            self.ui.say(f"You press the {obj.display_name()}. It does not appear to be a button, but it appreciates the attention.")
        elif verb == "push":
            self.ui.say(f"You push the {obj.display_name()}. It resists, philosophically.")
        elif verb == "pull":
            self.ui.say(f"You pull the {obj.display_name()}. Nothing moves except your expectations.")
        elif verb in ("switch", "switch_on", "switch_off", "turn"):
            self.ui.say(f"You {verb.replace('_', ' ')} the {obj.display_name()}. Nothing observable happens.")
        elif verb == "set":
            if not value:
                self.ui.say("Set it to what?")
            else:
                self.ui.say(f"The {obj.display_name()} does not accept that setting.")

    def do_wait(self) -> None:
        self.ui.say("Time passes. The Guide checks its watch. It is still a towel.")

    def do_attack(self, target: str | None) -> None:
        if not target:
            self.ui.say("You swing at the air. The air wins on points.")
            return
        npc = self.resolve_npc(target)
        if npc:
            if npc.on_attack:
                if npc.on_attack(self, npc):
                    return
            self.ui.say("Violence is the last refuge of the incompetent. The Guide recommends politics, or a towel.")
            return
        obj = self.resolve_object(target, "visible")
        if obj:
            self.ui.say(f"You attack the {obj.display_name()}. It is unmoved, in every sense.")
            return
        self.no_object(target)

    def do_throw(self, target: str | None, indirect: str | None = None) -> None:
        if not target:
            self.ui.say("Throw what?")
            return
        obj = self.resolve_object(target, "inventory")
        if not obj:
            self.ui.say("You are not carrying that.")
            return
        destination = self.resolve_any(indirect) if indirect else None
        if obj.on_throw:
            result = obj.on_throw(self, obj, destination)
            if isinstance(result, str):
                self.ui.say(result)
                return
            if result:
                return
        if isinstance(destination, NPC):
            self.state.obj_loc[obj.key] = destination.key
            self.ui.say(f"You throw the {obj.display_name()} at the {destination.display_name()}. They catch it, which is unsettling.")
        else:
            self.state.obj_loc[obj.key] = self.state.room
            self.ui.say(f"You throw the {obj.display_name()}. It lands on the floor with a disappointed clatter.")

    def do_sense(self, verb: str, target: str | None) -> None:
        if target:
            obj = self.resolve_object(target, "visible")
            if obj:
                if verb == "listen":
                    self.ui.say(f"You listen to the {obj.display_name()}. It says nothing, but it says it with conviction.")
                elif verb == "smell":
                    self.ui.say(f"The {obj.display_name()} smells of ozone, dust, and long-term decisions.")
                else:
                    self.ui.say(f"You touch the {obj.display_name()}. It is exactly as tangible as advertised.")
                return
        if verb == "listen":
            extra = self.room().extras.get("sound")
            self.ui.say(extra or "You hear the hum of civilization, or possibly air conditioning. On Trantor they are the same thing.")
        elif verb == "smell":
            extra = self.room().extras.get("smell")
            self.ui.say(extra or "It smells like ozone and bureaucracy, with a faint note of inevitability.")
        else:
            self.ui.say("You touch the nearest available reality. It holds still, which is polite of it.")

    def do_climb(self, target: str | None) -> None:
        if target:
            self.ui.say(f"You climb the {target}. The view is mostly the same, but with more vertigo.")
        else:
            self.ui.say("You climb nothing in particular. The Guide marks it as a bold lifestyle choice.")

    def do_sit(self, target: str | None) -> None:
        if target:
            self.ui.say(f"You sit on the {target}. It is exactly as comfortable as it looks, which is not saying much.")
        else:
            self.ui.say("You sit down. History continues without waiting.")

    def do_stand(self) -> None:
        self.ui.say("You stand up. The Guide respectfully updates your altitude.")

    def do_jump(self) -> None:
        self.ui.say("You jump. Local gravity is unimpressed.")

    def do_perform(self, verb: str) -> None:
        if verb == "sing":
            self.ui.say("You sing a verse of 'The Stars Are a Long Way from Home'. Somewhere, a minor Imperial censor wakes up.")
            self.achievement("A SONG FOR THE VOID", quiet=True)
        elif verb == "dance":
            self.ui.say("You dance. The Guide awards no points but respects the commitment.")
        else:
            self.ui.say("You pray to the Galactic Spirit. The Galactic Spirit, if present, does not reply. It has learned.")

    def do_yesno(self, verb: str) -> None:
        if verb == "yes":
            self.ui.say("You nod. The universe takes this as consent.")
        else:
            self.ui.say("You shake your head. The universe pretends not to be offended.")

    # ------------------------------------------------------------------
    # Meta commands
    # ------------------------------------------------------------------
    def do_help(self, topic: str | None = None) -> None:
        if topic:
            low = topic.lower()
            if "save" in low or "load" in low:
                self.ui.say("SAVE [name] writes a JSON save in " + str(SAVE_DIR) + ". LOAD [name] restores it. Autosave is written at each act boundary.")
                return
            if "guide" in low:
                self.ui.say("GUIDE lists unlocked entries. GUIDE <topic> reads one. Entries are unlocked by exploring, talking, and surviving.")
                return
            if "hint" in low:
                self.ui.say("HINT gives a contextual nudge and never reduces your score. If the first hint is too subtle, ask again.")
                return
            if "map" in low:
                self.ui.say("MAP draws the rooms you have visited. It is not a complete map of the Galaxy, which is larger and less well labelled.")
                return
        print_manual(self.ui)

    def do_about(self) -> None:
        self.ui.say()
        self.ui.say(self.ui.bold("THE HITCHHIKER'S GUIDE TO THE FOUNDATION"))
        self.ui.say("A fan-made CLI text adventure based on Isaac Asimov's Foundation trilogy.")
        self.ui.say()
        self.ui.say("Three acts. Three protagonists. One Plan, with a towel.")
        self.ui.say("Written in Python with no external dependencies.")
        self.ui.say()
        self.ui.say(self.ui.dim("This is an unauthorised fan work. It is not affiliated with the estate of"))
        self.ui.say(self.ui.dim("Isaac Asimov, the publishers, or the Second Foundation, which does not exist."))
        self.ui.say()
        self.ui.say(self.ui.italic('"Violence is the last refuge of the incompetent." — Salvor Hardin'))

    def do_version(self) -> None:
        from . import __version__

        self.ui.say(f"The Hitchhiker's Guide to the Foundation, version {__version__}.")

    def do_score(self) -> None:
        self.ui.say(
            f"Act {ROMAN.get(self.act_index, self.act_index + 1)} score: "
            f"{self.state.score}/{self.world.max_score}"
        )
        self.ui.say(
            f"Total: {self.total_score()}/{EPISODE_COUNT * 100} — "
            f"{self.rank_for(self.total_score(), EPISODE_COUNT * 100, final=True)}"
        )
        self.ui.say(
            self.ui.dim(
                f"Moves: {self.state.moves}    Deaths: {self.meta.deaths}    "
                f"Hints: {self.meta.hints}    Guide entries: {len(self.meta.guide_unlocked)}"
            )
        )
        if self.meta.achievements:
            self.ui.say(self.ui.dim("Achievements: " + ", ".join(sorted(self.meta.achievements))))

    def do_guide(self, topic: str | None = None) -> None:
        if not topic or topic.strip().lower() in ("list", "index", "topics", "all"):
            entries = sorted(self.meta.guide_unlocked)
            body = (
                f"Unlocked entries ({len(entries)}):\n\n"
                + ("\n".join("  " + entry for entry in entries) if entries else "  (none)")
                + "\n\nUse GUIDE <topic> to read one. The Guide is not responsible for"
                " entries that have been sealed by the Second Foundation, the First"
                " Foundation, or a sufficiently determined librarian."
            )
            self.ui.box("THE GUIDE", body)
            return
        key = guide.find(topic)
        if key is None:
            self.ui.say(f"The Guide has no entry on {topic!r}. It has an entry on everything else, which is not the same thing.")
            return
        if key not in self.meta.guide_unlocked:
            self.ui.say(f"The Guide's entry on {key} is sealed. The seal is bureaucratic, not magical: make progress.")
            return
        self.ui.box(f"THE GUIDE — {key}", guide.ENTRIES[key])

    def do_hint(self) -> None:
        text = ""
        if self.world.hints:
            text = self.world.hints(self) or ""
        if not text:
            text = "Look at everything, talk to everyone, and try the object the Guide keeps mentioning: the towel."
        self.meta.hints += 1
        self.state.hint_count += 1
        self.ui.hint("HINT: " + text)
        if self.meta.hints == 1:
            self.ui.say(self.ui.dim("(Hints never reduce your score. They only reduce the Guide's opinion of you.)"))

    def do_map(self) -> None:
        visited = [
            room for key, room in self.world.rooms.items() if key in self.state.seen
        ]
        coords = {(room.coords): room for room in visited}
        if len(coords) <= 1:
            self.ui.say("You have visited: " + ", ".join(room.name for room in visited) + ".")
            self.ui.say("The Guide's cartography department is still unfolding the map.")
            return
        xs = [x for x, _ in coords]
        ys = [y for _, y in coords]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = 11
        if (max_x - min_x + 1) * (width + 2) > self.ui.width:
            width = 7
        self.ui.say(self.ui.bold("MAP"))
        for y in range(min_y, max_y + 1):
            cells: list[str] = []
            for x in range(min_x, max_x + 1):
                room = coords.get((x, y))
                if not room:
                    cells.append(" " * width)
                    continue
                label = (room.map_label or room.key)[: width - 2]
                if room.key == self.state.room:
                    cells.append(("[@" + label + "]").ljust(width))
                else:
                    cells.append(("[" + label + "]").ljust(width))
            self.ui.raw(" " + " ".join(cells))
        self.ui.say(self.ui.dim("@ = you. Only visited rooms are shown."))

    def do_save(self, name: str | None = None) -> None:
        self.save(name)

    def do_load(self, name: str | None = None) -> None:
        if self.load_file(name):
            self._skip_after = True

    def do_restart(self) -> None:
        self.state.pending = "restart"
        self.ui.say(
            "This will erase the current journey and start again. Type YES to confirm, or anything else to continue."
        )

    def do_undo(self) -> None:
        if not self.snapshots:
            self.ui.say("There is nothing to undo. The Guide has already forgotten the beginning.")
            return
        self.state = self.snapshots.pop()
        self.ui.say(self.ui.dim("The Guide rewinds one turn. It is getting good at this."))
        self.status_line()

    def do_verbose(self) -> None:
        self.state.verbose = True
        self.ui.say("Verbose descriptions enabled. The Guide clears its throat.")

    def do_brief(self) -> None:
        self.state.verbose = False
        self.ui.say("Brief descriptions enabled. The Guide will now be concise, by its standards.")

    def do_status(self) -> None:
        self.status_line()
        self.ui.say(
            self.ui.dim(
                f"Act {ROMAN.get(self.act_index, self.act_index + 1)}: {self.world.title} — "
                f"{self.world.protagonist}. Moves: {self.state.moves}."
            )
        )

    def do_achievements(self) -> None:
        if not self.meta.achievements:
            self.ui.say("The Guide has not yet been impressed. It is patient, in a geological sense.")
            return
        self.ui.say(self.ui.bold("ACHIEVEMENTS"))
        for name in sorted(self.meta.achievements):
            self.ui.say("  " + name)

    def do_quit(self) -> None:
        self.ui.say()
        self.ui.say(self.ui.dim("The Guide closes. Don't panic."))
        self.running = False
        self._skip_after = True

    # ------------------------------------------------------------------
    # Easter eggs
    # ------------------------------------------------------------------
    def do_panic(self) -> None:
        self.unlock_guide("DON'T PANIC", quiet=True)
        self.achievement("DON'T PANIC", quiet=True)
        self.ui.box("DON'T PANIC", "In large, friendly letters.", style="green")

    def do_forty_two(self) -> None:
        self.unlock_guide("42", quiet=True)
        self.achievement("THE ANSWER", quiet=True)
        self.ui.say("42.")
        self.ui.say(self.ui.dim("The ultimate question remains unknown. The Guide suggests it was probably about towels."))

    def do_xyzzy(self) -> None:
        self.unlock_guide("42", quiet=True)
        if "XYZZY" not in self.meta.achievements:
            self.achievement("XYZZY", quiet=True)
            self.ui.say("A hollow voice says: 'Fool.'")
            self.ui.say(self.ui.dim("The Guide notes that XYZZY is not a recognised command in this edition. It is, however, a recognised state of mind."))
        else:
            self.ui.say("The hollow voice is getting tired of you.")

    def do_towel(self) -> None:
        towels = [
            key for key, obj in self.world.objects.items()
            if "towel" in obj.names or "towel" in key
        ]
        if any(self.is_carried(key) for key in towels):
            self.ui.say("You clutch your towel. The universe feels marginally more manageable.")
            self.achievement("TOWEL", quiet=True)
        else:
            self.ui.say("You wish you had a towel. The Guide makes a note in your permanent record.")

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------
    def dispatch(self, cmd: Command) -> None:
        verb = cmd.verb
        if verb == "help":
            self.do_help(cmd.dobj)
            return
        if verb == "about":
            self.do_about()
            return
        if verb == "version":
            self.do_version()
            return
        if verb == "score":
            self.do_score()
            return
        if verb == "inventory":
            self.do_inventory()
            return
        if verb == "guide":
            self.do_guide(cmd.dobj)
            return
        if verb == "hint":
            self.do_hint()
            return
        if verb == "map":
            self.do_map()
            return
        if verb == "save":
            self.do_save(cmd.dobj)
            return
        if verb == "load":
            self.do_load(cmd.dobj)
            return
        if verb == "restart":
            self.do_restart()
            return
        if verb == "undo":
            self.do_undo()
            return
        if verb == "verbose":
            self.do_verbose()
            return
        if verb == "brief":
            self.do_brief()
            return
        if verb == "status":
            self.do_status()
            return
        if verb == "achievements":
            self.do_achievements()
            return
        if verb == "quit":
            self.do_quit()
            return

        if self.world.on_command:
            result = self.world.on_command(self, verb, cmd)
            if isinstance(result, str):
                self.ui.say(result)
                return
            if result:
                return

        if verb == "look":
            self.do_look(cmd.dobj)
        elif verb == "examine":
            self.do_examine(cmd.dobj)
        elif verb == "read":
            self.do_read(cmd.dobj)
        elif verb == "search":
            self.do_search(cmd.dobj)
        elif verb == "go":
            self.do_go(cmd.dobj or "")
        elif verb == "enter":
            self.do_enter(cmd.dobj)
        elif verb == "exit":
            self.do_exit(cmd.dobj)
        elif verb == "board":
            self.do_board(cmd.dobj)
        elif verb == "take":
            self.do_take(cmd.dobj)
        elif verb == "drop":
            self.do_drop(cmd.dobj)
        elif verb == "put":
            self.do_put(cmd.dobj, cmd.prep, cmd.iobj)
        elif verb == "inventory":
            self.do_inventory()
        elif verb == "open":
            self.do_open(cmd.dobj)
        elif verb == "close":
            self.do_close(cmd.dobj)
        elif verb == "unlock":
            self.do_unlock(cmd.dobj, cmd.iobj)
        elif verb == "lock":
            self.do_lock(cmd.dobj, cmd.iobj)
        elif verb == "wear":
            self.do_wear(cmd.dobj)
        elif verb == "remove":
            self.do_remove(cmd.dobj)
        elif verb == "give":
            self.do_give(cmd.dobj, cmd.iobj)
        elif verb == "show":
            self.do_show(cmd.dobj, cmd.iobj)
        elif verb == "talk":
            self.do_talk(cmd.dobj)
        elif verb == "ask":
            self.do_ask(cmd.dobj, cmd.iobj)
        elif verb == "say":
            self.do_say(cmd.dobj)
        elif verb == "type":
            self.do_type(cmd.dobj)
        elif verb == "use":
            self.do_use(cmd.dobj, cmd.iobj)
        elif verb in ("push", "pull", "press", "switch", "switch_on", "switch_off", "turn"):
            self._manipulate(verb, cmd.dobj)
        elif verb == "set":
            self._manipulate("set", cmd.dobj, cmd.iobj)
        elif verb == "wait":
            self.do_wait()
        elif verb == "listen":
            self.do_sense("listen", cmd.dobj)
        elif verb == "smell":
            self.do_sense("smell", cmd.dobj)
        elif verb == "touch":
            self.do_sense("touch", cmd.dobj)
        elif verb == "climb":
            self.do_climb(cmd.dobj)
        elif verb == "sit":
            self.do_sit(cmd.dobj)
        elif verb == "stand":
            self.do_stand()
        elif verb == "jump":
            self.do_jump()
        elif verb == "attack":
            self.do_attack(cmd.dobj)
        elif verb == "throw":
            self.do_throw(cmd.dobj, cmd.iobj)
        elif verb in ("sing", "dance", "pray"):
            self.do_perform(verb)
        elif verb == "wake":
            self.ui.say("You are awake. The Galaxy is still there. The Guide considers this a mixed result.")
        elif verb == "lie":
            self.ui.say("You lie down. The floor is not impressed, but it is supportive.")
        elif verb in ("yes", "no"):
            self.do_yesno(verb)
        elif verb == "panic":
            self.do_panic()
        elif verb == "forty_two":
            self.do_forty_two()
        elif verb == "xyzzy":
            self.do_xyzzy()
        elif verb == "towel":
            self.do_towel()
        else:
            self.unknown_command(cmd)

    def do_enter(self, target: str | None) -> None:
        if not target:
            self.ui.say("Enter what?")
            return
        direction = target.strip()
        if direction in ("north", "south", "east", "west", "up", "down", "in", "out"):
            self.do_go(direction)
            return
        found = self.find_exit(self.room(), direction)
        if found:
            self.do_go(direction)
            return
        obj = self.resolve_object(direction, "visible")
        if obj:
            if obj.on_use:
                result = obj.on_use(self, obj, None)
                if result:
                    return
            self.ui.say(f"You can't enter the {obj.display_name()}. The Guide checked the dimensions.")
            return
        self.no_object(direction)

    def do_exit(self, target: str | None = None) -> None:
        if target:
            found = self.find_exit(self.room(), target)
            if found:
                self.do_go(target)
                return
            obj = self.resolve_object(target, "visible")
            if obj:
                self.ui.say(f"You leave the {obj.display_name()} behind. It does not appear to mind.")
                return
        found = self.find_exit(self.room(), "out")
        if found:
            self.do_go("out")
        else:
            self.ui.say("There is no obvious exit. The Guide suggests making one, but it is not insured for structural damage.")

    def do_board(self, target: str | None) -> None:
        if not target:
            self.ui.say("Board what?")
            return
        found = self.find_exit(self.room(), target)
        if found:
            self.do_go(target)
            return
        obj = self.resolve_object(target, "visible")
        if obj:
            if obj.on_use:
                result = obj.on_use(self, obj, None)
                if result:
                    return
            self.ui.say(f"You board the {obj.display_name()}. It does not go anywhere, but you feel more nautical.")
            return
        self.no_object(target)

    def unknown_command(self, cmd: Command) -> None:
        verb = cmd.verb
        suggestions = difflib.get_close_matches(verb, list(VERBS), n=2, cutoff=0.6)
        text = f"The Guide does not know the word {verb!r}."
        if suggestions:
            text += " It wonders whether you mean " + join_names(s.upper() for s in suggestions) + "."
        else:
            text += " Try HELP, or a verb with a better survival rate."
        self.ui.say(text)

    # ------------------------------------------------------------------
    # Saving and loading
    # ------------------------------------------------------------------
    def _save_path(self, name: str | None) -> Path:
        name = (name or "quicksave").strip()
        if not name:
            name = "quicksave"
        if name.lower().endswith(".json"):
            name = name[:-5]
        path = Path(name)
        if path.is_absolute() or "/" in name or "\\" in name:
            if not path.is_absolute():
                path = SAVE_DIR / path
        else:
            path = SAVE_DIR / (name + ".json")
        return path

    def save(self, name: str | None = None, quiet: bool = False) -> bool:
        path = self._save_path(name)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "format": SAVE_FORMAT,
                "version": SAVE_VERSION,
                "act": self.act_index,
                "meta": self.meta.to_dict(),
                "state": self.state.to_dict(),
                "saved_at": datetime.now().isoformat(timespec="seconds"),
            }
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError as exc:
            self.ui.error(f"The Guide could not write the save: {exc}")
            return False
        if not quiet:
            self.ui.say(self.ui.green(f"Game saved to {path}."))
        return True

    def load_file(self, name: str | None = None) -> bool:
        path = self._save_path(name)
        if not path.exists():
            available = sorted(p.stem for p in SAVE_DIR.glob("*.json")) if SAVE_DIR.exists() else []
            self.ui.error(f"No save file at {path}.")
            if available:
                self.ui.say("Available saves: " + ", ".join(available) + ".")
            return False
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            self.ui.error(f"The Guide could not read that save: {exc}")
            return False
        if data.get("format") != SAVE_FORMAT or data.get("version") != SAVE_VERSION:
            self.ui.error("That save was written by a different edition of the Guide. It is probably from a parallel universe.")
            return False
        try:
            act_index = int(data["act"])
            world = load_episode(act_index)
            meta = Meta.from_dict(data.get("meta", {}))
            state = ActState.from_dict(data.get("state", {}))
        except (KeyError, ValueError, TypeError, IndexError) as exc:
            self.ui.error(f"That save is damaged: {exc}")
            return False
        if state.room not in world.rooms:
            self.ui.error("That save points to a room the Guide cannot find. Try an older save, or a newer universe.")
            return False
        for key, obj in world.objects.items():
            state.obj_loc.setdefault(key, obj.location)
            state.obj_open.setdefault(key, obj.open)
            state.obj_locked.setdefault(key, obj.locked)
        self.act_index = act_index
        self.world = world
        self.meta = meta
        self.state = state
        self.snapshots = []
        self._end_handled = False
        self._skip_after = True
        self.running = True
        self.ui.say(self.ui.green(f"Game loaded from {path}."))
        if self.state.finished:
            self.ui.say(self.ui.dim("This save is at the end of an act. The Guide will turn the page."))
        else:
            self.ui.say()
            self.describe_room(False)
        return True
