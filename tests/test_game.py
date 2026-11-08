"""Automated tests for The Hitchhiker's Guide to the Foundation.

Run with:

    uv run python -m unittest discover -s tests -v
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from foundation_guide import engine, guide
from foundation_guide.engine import Game
from foundation_guide.episodes import EPISODE_COUNT, load_episode
from foundation_guide.parser import parse
from foundation_guide.ui import UI

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"


def load_commands(name: str) -> list[str]:
    commands: list[str] = []
    for line in (TESTS / name).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            commands.append(line)
    return commands


def new_game(act_index: int = 0) -> Game:
    return Game(UI(color=False, script=[]), act_index=act_index, debug=True)


def play_script(act_index: int, commands: list[str]) -> tuple[Game, str]:
    """Play commands one at a time without advancing to the next act."""
    game = new_game(act_index)
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        game.start_act()
        for raw in commands:
            if game.state.finished:
                break
            game.execute(raw)
    return game, output.getvalue()


class ParserTests(unittest.TestCase):
    def test_direction_abbreviation(self) -> None:
        command = parse("n")
        self.assertIsNotNone(command)
        assert command is not None
        self.assertEqual(command.verb, "go")
        self.assertEqual(command.dobj, "north")

    def test_articles_and_compound_verbs(self) -> None:
        command = parse("pick up the towel")
        assert command is not None
        self.assertEqual(command.verb, "take")
        self.assertEqual(command.dobj, "the towel")

    def test_put_in(self) -> None:
        command = parse("put the prime radiant in the towel")
        assert command is not None
        self.assertEqual(
            (command.verb, command.dobj, command.iobj),
            ("put", "the prime radiant", "the towel"),
        )

    def test_ask_about(self) -> None:
        command = parse("ask Seldon about psychohistory")
        assert command is not None
        self.assertEqual((command.verb, command.dobj, command.iobj), ("ask", "seldon", "psychohistory"))

    def test_use_on(self) -> None:
        command = parse("use the Visi-Sonor on Mis")
        assert command is not None
        self.assertEqual((command.verb, command.dobj, command.iobj), ("use", "the visi-sonor", "mis"))

    def test_set_to(self) -> None:
        command = parse("set course to Trantor")
        assert command is not None
        self.assertEqual((command.verb, command.dobj, command.iobj), ("set", "course", "trantor"))

    def test_shoot_is_attack(self) -> None:
        command = parse("shoot Mis")
        assert command is not None
        self.assertEqual((command.verb, command.dobj), ("attack", "mis"))

    def test_polite_prefix_and_quotes(self) -> None:
        command = parse('please say "don\'t panic"')
        assert command is not None
        self.assertEqual(command.verb, "say")
        self.assertEqual(command.dobj, "don't panic")

    def test_blank_input(self) -> None:
        self.assertIsNone(parse("   "))


class WorldIntegrityTests(unittest.TestCase):
    def test_episode_count(self) -> None:
        self.assertEqual(EPISODE_COUNT, 3)

    def test_all_worlds_are_well_formed(self) -> None:
        for index in range(EPISODE_COUNT):
            with self.subTest(act=index):
                world = load_episode(index)
                self.assertEqual(world.max_score, 100)
                self.assertIn(world.start_room, world.rooms)
                self.assertTrue(world.title)
                self.assertTrue(world.protagonist)
                self.assertTrue(world.intro)

                for key, room in world.rooms.items():
                    self.assertEqual(key, room.key)
                    for direction, exit_ in room.exits.items():
                        self.assertIn(
                            exit_.dest,
                            world.rooms,
                            f"{key} exit {direction!r} points at missing room {exit_.dest!r}",
                        )

                valid_locations = set(world.rooms) | set(world.objects) | {None, "player"}
                for key, obj in world.objects.items():
                    self.assertEqual(key, obj.key)
                    self.assertIn(
                        obj.location,
                        valid_locations,
                        f"object {key!r} has invalid location {obj.location!r}",
                    )

                for key, npc in world.npcs.items():
                    self.assertEqual(key, npc.key)
                    self.assertIn(
                        npc.location,
                        set(world.rooms) | {None},
                        f"NPC {key!r} has invalid location {npc.location!r}",
                    )

                for guide_key in world.guide_keys:
                    self.assertTrue(
                        guide.exists(guide_key),
                        f"unknown guide entry {guide_key!r} in act {index + 1}",
                    )


class WalkthroughTests(unittest.TestCase):
    def assert_act_won(self, act_index: int, script: str) -> Game:
        game, output = play_script(act_index, load_commands(script))
        self.assertTrue(game.state.finished, output[-2000:])
        self.assertEqual(game.state.score, 100, output[-2000:])
        self.assertEqual(game.meta.deaths, 0)
        return game

    def test_act_one_scores_100(self) -> None:
        self.assert_act_won(0, "walkthrough_act1.txt")

    def test_act_two_faith_ending_scores_100(self) -> None:
        game = self.assert_act_won(1, "walkthrough_act2.txt")
        self.assertEqual(game.meta.doctrine, "faith")
        self.assertEqual(game.meta.ending, "act2_faith")

    def test_act_two_trade_ending_scores_100(self) -> None:
        game = self.assert_act_won(1, "walkthrough_act2_trade.txt")
        self.assertEqual(game.meta.doctrine, "trade")
        self.assertEqual(game.meta.ending, "act2_trade")

    def test_act_three_quiet_ending_scores_100(self) -> None:
        game = self.assert_act_won(2, "walkthrough_act3.txt")
        self.assertEqual(game.meta.ending, "act3_quiet")

    def test_act_three_open_ending_scores_100(self) -> None:
        game = self.assert_act_won(2, "walkthrough_act3_open.txt")
        self.assertEqual(game.meta.ending, "act3_open")

    def test_full_game_scores_300(self) -> None:
        commands = (
            load_commands("walkthrough_act1.txt")
            + load_commands("walkthrough_act2.txt")
            + load_commands("walkthrough_act3.txt")
        )
        game = Game(UI(color=False, script=commands), debug=True)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            game.start_new()
            game.run()
        self.assertEqual(
            game.meta.act_scores,
            {0: 100, 1: 100, 2: 100},
            output.getvalue()[-3000:],
        )
        self.assertEqual(game.meta.total_score, 300)
        self.assertEqual(game.meta.ending, "act3_quiet")
        self.assertEqual(game.meta.deaths, 0)


class EngineBehaviourTests(unittest.TestCase):
    def test_hint_never_reduces_score(self) -> None:
        game = new_game(0)
        with contextlib.redirect_stdout(io.StringIO()):
            game.start_act()
            game.execute("hint")
        self.assertEqual(game.state.score, 0)
        self.assertEqual(game.meta.hints, 1)

    def test_pronoun_refers_to_last_object(self) -> None:
        game = new_game(0)
        with contextlib.redirect_stdout(io.StringIO()):
            game.start_act()
            game.execute("take suitcase")
        obj = game.resolve_object("it")
        self.assertIsNotNone(obj)
        assert obj is not None
        self.assertEqual(obj.key, "suitcase")

    def test_death_rewinds_one_turn(self) -> None:
        game = new_game(0)
        with contextlib.redirect_stdout(io.StringIO()):
            game.start_act()
            game.execute("look")
            room = game.state.room
            score = game.state.score
            game.death("A test death.")
        self.assertEqual(game.meta.deaths, 1)
        self.assertEqual(game.state.room, room)
        self.assertEqual(game.state.score, score)

    def test_save_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            save_dir = Path(temp_dir)
            with mock.patch.object(engine, "SAVE_DIR", save_dir):
                game = new_game(0)
                with contextlib.redirect_stdout(io.StringIO()):
                    game.start_act()
                    game.execute("take suitcase")
                    game.execute("open suitcase")
                    game.execute("read letter")
                    game.execute("use visa on pedestal")
                    expected_room = game.state.room
                    expected_score = game.state.score
                    expected_loc = dict(game.state.obj_loc)
                    self.assertTrue(game.save("slot"))
                    self.assertTrue((save_dir / "slot.json").exists())
                    game.execute("north")
                    self.assertNotEqual(game.state.room, expected_room)
                    self.assertTrue(game.load_file("slot"))
                self.assertEqual(game.state.room, expected_room)
                self.assertEqual(game.state.score, expected_score)
                self.assertEqual(game.state.obj_loc, expected_loc)

    def test_load_missing_save_fails_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(engine, "SAVE_DIR", Path(temp_dir)):
                game = new_game(0)
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertFalse(game.load_file("does-not-exist"))

    def test_guide_lookup_is_forgiving(self) -> None:
        self.assertEqual(guide.find("star's end"), "STAR'S END")
        self.assertEqual(guide.find("visi sonor"), "VISI-SONOR")
        self.assertIsNone(guide.find("a topic from a parallel universe"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
