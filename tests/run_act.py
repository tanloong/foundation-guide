"""Run a single act directly from a command script (developer tool)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from foundation_guide.engine import Game
from foundation_guide.ui import UI


def load_script(path: Path) -> list[str]:
    commands: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        commands.append(line)
    return commands


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("act", type=int, help="0, 1, or 2")
    parser.add_argument("script", type=Path)
    parser.add_argument("--width", type=int, default=90)
    args = parser.parse_args()

    commands = load_script(args.script)
    ui = UI(color=False, script=[], width=args.width)
    game = Game(ui, act_index=args.act, debug=True)
    game.start_act()
    for raw in commands:
        if game.state.finished:
            break
        game.execute(raw)
    if not game.state.finished:
        print("\n(The script ended before the act was completed.)")
    print(f"\nFINAL ACT SCORE: {game.state.score}/{game.world.max_score}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
