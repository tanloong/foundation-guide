"""A small, forgiving parser for a classic text adventure.

It understands commands such as::

    take the towel
    put the prime radiant in the towel
    give the decoy to commissioner chen
    ask seldon about psychohistory
    use the towel on the major-domo
    set the dial to core
    n
    don't panic
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Command:
    verb: str
    dobj: str | None = None
    prep: str | None = None
    iobj: str | None = None
    raw: str = ""


DIRECTIONS = {
    "n": "north",
    "north": "north",
    "s": "south",
    "south": "south",
    "e": "east",
    "east": "east",
    "w": "west",
    "west": "west",
    "ne": "northeast",
    "northeast": "northeast",
    "nw": "northwest",
    "northwest": "northwest",
    "se": "southeast",
    "southeast": "southeast",
    "sw": "southwest",
    "southwest": "southwest",
    "u": "up",
    "up": "up",
    "d": "down",
    "down": "down",
    "in": "in",
    "out": "out",
}

VERBS = {
    "look": "look",
    "l": "look",
    "examine": "examine",
    "x": "examine",
    "inspect": "examine",
    "check": "examine",
    "take": "take",
    "get": "take",
    "grab": "take",
    "carry": "take",
    "drop": "drop",
    "discard": "drop",
    "release": "drop",
    "inventory": "inventory",
    "i": "inventory",
    "inv": "inventory",
    "open": "open",
    "close": "close",
    "shut": "close",
    "unlock": "unlock",
    "lock": "lock",
    "read": "read",
    "search": "search",
    "find": "search",
    "wear": "wear",
    "don": "wear",
    "remove": "remove",
    "doff": "remove",
    "give": "give",
    "offer": "give",
    "hand": "give",
    "show": "show",
    "talk": "talk",
    "speak": "talk",
    "ask": "ask",
    "tell": "ask",
    "use": "use",
    "apply": "use",
    "push": "push",
    "shove": "push",
    "pull": "pull",
    "press": "press",
    "turn": "turn",
    "switch": "switch",
    "flip": "switch",
    "set": "set",
    "type": "type",
    "enter": "enter",
    "exit": "exit",
    "leave": "exit",
    "board": "board",
    "go": "go",
    "walk": "go",
    "run": "go",
    "move": "go",
    "climb": "climb",
    "sit": "sit",
    "stand": "stand",
    "jump": "jump",
    "wait": "wait",
    "z": "wait",
    "listen": "listen",
    "hear": "listen",
    "smell": "smell",
    "sniff": "smell",
    "touch": "touch",
    "feel": "touch",
    "attack": "attack",
    "kill": "attack",
    "hit": "attack",
    "fight": "attack",
    "shoot": "attack",
    "fire": "attack",
    "blast": "attack",
    "throw": "throw",
    "say": "say",
    "answer": "say",
    "shout": "say",
    "whisper": "say",
    "sing": "sing",
    "dance": "dance",
    "pray": "pray",
    "help": "help",
    "hint": "hint",
    "guide": "guide",
    "map": "map",
    "score": "score",
    "save": "save",
    "load": "load",
    "quit": "quit",
    "q": "quit",
    "restart": "restart",
    "undo": "undo",
    "verbose": "verbose",
    "brief": "brief",
    "status": "status",
    "about": "about",
    "credits": "about",
    "version": "version",
    "achievements": "achievements",
    "yes": "yes",
    "y": "yes",
    "no": "no",
}

# Compound verbs must be checked before the first word is looked up.
COMPOUNDS = [
    ("pick up", "take"),
    ("put down", "drop"),
    ("look at", "examine"),
    ("look under", "search"),
    ("look behind", "search"),
    ("look inside", "search"),
    ("look in", "search"),
    ("look around", "look"),
    ("search for", "search"),
    ("talk to", "talk"),
    ("speak to", "talk"),
    ("speak with", "talk"),
    ("take off", "remove"),
    ("put on", "wear"),
    ("turn on", "switch_on"),
    ("turn off", "switch_off"),
    ("switch on", "switch_on"),
    ("switch off", "switch_off"),
    ("go to", "go"),
    ("walk to", "go"),
    ("get on", "board"),
    ("get in", "board"),
    ("get off", "exit"),
    ("get out", "exit"),
    ("climb up", "climb"),
    ("climb down", "climb"),
    ("wake up", "wake"),
    ("stand up", "stand"),
    ("sit down", "sit"),
    ("lie down", "lie"),
]

POLITE_PREFIXES = (
    "please ",
    "i want to ",
    "i'd like to ",
    "i would like to ",
    "can i ",
    "could i ",
    "try to ",
)


def normalise(raw: str) -> str:
    text = raw.strip().lower()
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace(",", " ")
    text = re.sub(r"\s+", " ", text)
    # Strip a final full stop or exclamation mark, but keep question marks in
    # SAY text (they are harmless either way).
    text = re.sub(r"[.!]+$", "", text).strip()
    for prefix in POLITE_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix) :].strip()
            break
    return text


def strip_quotes(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1].strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return text[1:-1].strip()
    return text


def split_on(rest: str, markers: list[str]) -> tuple[str, str | None, str | None]:
    """Split ``rest`` at the first ``marker`` surrounded by spaces."""
    for marker in markers:
        needle = f" {marker} "
        idx = rest.find(needle)
        if idx > 0:
            left = rest[:idx].strip()
            right = rest[idx + len(needle) :].strip()
            if left and right:
                return left, marker, right
    return rest.strip(), None, None


def parse(raw: str) -> Command | None:
    text = normalise(raw)
    if not text:
        return None

    # Special un-lookup-able incantations.
    if text in ("don't panic", "dont panic", "do not panic"):
        return Command("panic", raw=raw)
    if text == "xyzzy":
        return Command("xyzzy", raw=raw)
    if text in ("42", "forty two", "forty-two"):
        return Command("forty_two", raw=raw)

    words = text.split()
    if words[0] in DIRECTIONS and len(words) == 1:
        return Command("go", DIRECTIONS[words[0]], raw=raw)

    # Multi-word verbs.
    for phrase, verb in COMPOUNDS:
        if text == phrase:
            return Command(verb, raw=raw)
        if text.startswith(phrase + " "):
            rest = text[len(phrase) + 1 :].strip()
            return _parse_for_verb(verb, rest, raw)

    first = words[0]
    verb = VERBS.get(first, first)
    rest = " ".join(words[1:]).strip()
    return _parse_for_verb(verb, rest, raw)


def _parse_for_verb(verb: str, rest: str, raw: str) -> Command:
    if not rest:
        return Command(verb, raw=raw)

    if verb == "go":
        if rest.startswith("to "):
            rest = rest[3:].strip()
        if rest in DIRECTIONS:
            rest = DIRECTIONS[rest]
        return Command("go", rest, raw=raw)

    if verb in ("enter", "exit", "board", "climb", "sit", "stand", "jump", "wait"):
        return Command(verb, rest, raw=raw)

    if verb in ("say", "type"):
        return Command(verb, strip_quotes(rest), raw=raw)

    if verb == "look":
        # LOOK AT X is the common case; LOOK UNDER X etc. are handled by
        # compounds, but accept them here too.
        for prep in ("at", "under", "behind", "inside", "in", "on"):
            if rest.startswith(prep + " "):
                target = rest[len(prep) + 1 :].strip()
                if prep == "at":
                    return Command("examine", target, raw=raw)
                return Command("search", target, prep=prep, raw=raw)
        if rest == "at":
            return Command("look", raw=raw)
        return Command("examine", rest, raw=raw)

    if verb == "search":
        if rest.startswith("for "):
            rest = rest[4:].strip()
        return Command("search", rest, raw=raw)

    if verb == "ask":
        dobj, prep, iobj = split_on(rest, ["about", "regarding", "concerning"])
        if prep:
            return Command("ask", dobj, prep, iobj, raw=raw)
        return Command("ask", rest, raw=raw)

    if verb in ("give", "show", "hand", "offer"):
        dobj, prep, iobj = split_on(rest, ["to"])
        if prep:
            return Command(verb, dobj, prep, iobj, raw=raw)
        return Command(verb, rest, raw=raw)

    if verb in ("use", "apply"):
        dobj, prep, iobj = split_on(rest, ["on", "with", "upon"])
        if prep:
            return Command("use", dobj, prep, iobj, raw=raw)
        return Command("use", rest, raw=raw)

    if verb in ("put", "insert", "place"):
        dobj, prep, iobj = split_on(rest, ["in", "into", "inside", "on", "under"])
        if prep:
            return Command("put", dobj, prep, iobj, raw=raw)
        return Command("put", rest, raw=raw)

    if verb in ("unlock", "lock", "open", "close"):
        dobj, prep, iobj = split_on(rest, ["with", "using"])
        if prep:
            return Command(verb, dobj, prep, iobj, raw=raw)
        return Command(verb, rest, raw=raw)

    if verb == "throw":
        dobj, prep, iobj = split_on(rest, ["at", "to"])
        if prep:
            return Command("throw", dobj, prep, iobj, raw=raw)
        return Command("throw", rest, raw=raw)

    if verb == "set":
        dobj, prep, iobj = split_on(rest, ["to", "at"])
        if prep:
            return Command("set", dobj, prep, iobj, raw=raw)
        return Command("set", rest, raw=raw)

    if verb == "turn":
        # TURN LAMP ON / TURN LAMP OFF
        if rest.endswith(" on"):
            return Command("switch_on", rest[:-3].strip(), raw=raw)
        if rest.endswith(" off"):
            return Command("switch_off", rest[:-4].strip(), raw=raw)
        dobj, prep, iobj = split_on(rest, ["to", "at"])
        if prep:
            return Command("set", dobj, prep, iobj, raw=raw)
        return Command("turn", rest, raw=raw)

    if verb == "switch":
        if rest.startswith("on "):
            return Command("switch_on", rest[3:].strip(), raw=raw)
        if rest.startswith("off "):
            return Command("switch_off", rest[4:].strip(), raw=raw)
        if rest.endswith(" on"):
            return Command("switch_on", rest[:-3].strip(), raw=raw)
        if rest.endswith(" off"):
            return Command("switch_off", rest[:-4].strip(), raw=raw)
        return Command("switch", rest, raw=raw)

    if verb in ("push", "pull", "press"):
        # PUSH BUTTON, PULL LEVER, PRESS BUTTON; no indirect object needed.
        dobj, prep, iobj = split_on(rest, ["on", "with"])
        if prep:
            return Command(verb, dobj, prep, iobj, raw=raw)
        return Command(verb, rest, raw=raw)

    if verb == "read":
        return Command("read", rest, raw=raw)

    return Command(verb, rest, raw=raw)
