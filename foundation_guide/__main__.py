"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .engine import SAVE_DIR, Game, print_manual
from .ui import UI


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="foundation-guide",
        description="The Hitchhiker's Guide to the Foundation: a CLI text adventure.",
    )
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colour")
    parser.add_argument("--ascii", action="store_true", help="use ASCII box drawing")
    parser.add_argument("--width", type=int, default=None, help="wrap width (default: terminal width)")
    parser.add_argument("--script", type=Path, default=None, help="play commands from a file (testing/demo)")
    parser.add_argument(
        "--load",
        nargs="?",
        const="autosave",
        default=None,
        help="load a save by name (default: autosave)",
    )
    parser.add_argument("--debug", action="store_true", help="show tracebacks instead of Guide aphorisms")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def load_script(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    commands: list[str] = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        commands.append(line)
    return commands


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    script_commands = None
    if args.script:
        try:
            script_commands = load_script(args.script)
        except OSError as exc:
            print(f"Could not read script: {exc}", file=sys.stderr)
            return 1

    ui = UI(
        color=not args.no_color,
        ascii_only=args.ascii,
        script=script_commands,
        width=args.width,
    )

    if script_commands is not None:
        game = Game(ui, debug=args.debug)
        if args.load:
            if not game.load_file(args.load):
                return 1
        else:
            game.start_new()
        game.run()
        return 0

    # Interactive menu.
    has_save = (SAVE_DIR / "autosave.json").exists()
    while True:
        choice = ui.menu(has_save)
        if choice == "quit":
            ui.say()
            ui.say("Don't panic.")
            return 0
        if choice == "help":
            print_manual(ui)
            ui.pause("Press ENTER to return to the menu...")
            continue
        game = Game(ui, debug=args.debug)
        if choice == "load":
            if not game.load_file("autosave"):
                ui.error("The autosave could not be loaded. Starting a new journey instead.")
                game.start_new()
        else:
            game.start_new()
        game.run()
        ui.say()
        try:
            again = input(ui.dim("Play again? [y/N] ")).strip().lower()
        except EOFError:
            return 0
        if again not in ("y", "yes"):
            ui.say()
            ui.say("So long, and thanks for all the psychohistory.")
            return 0
        has_save = (SAVE_DIR / "autosave.json").exists()


if __name__ == "__main__":
    raise SystemExit(main())
