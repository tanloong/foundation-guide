# THE HITCHHIKER'S GUIDE TO THE FOUNDATION

[![PyPI](https://img.shields.io/pypi/v/foundation-guide.svg)](https://pypi.org/project/foundation-guide/) [![Python](https://img.shields.io/pypi/pyversions/foundation-guide.svg)](https://pypi.org/project/foundation-guide/)

A text adventure that runs in your terminal. Three protagonists, three acts, thirty-four locations, one hundred and forty-six objects, twenty-three characters, and one towel.

The story takes place in the universe of Isaac Asimov's *Foundation* trilogy, narrated with the dry, cosmic absurdity of Douglas Adams' *The Hitchhiker's Guide to the Galaxy*. You play Gaal Dornick, Salvor Hardin, and Bayta Darell in turn — surviving, negotiating, and solving puzzles in the cracks of psychohistory, while deciding whether the future of the galaxy should be handed to a man in a clown suit.

> This is a fan-made work, unaffiliated with the Asimov estate, the publishers, or the Second Foundation (which does not exist).

---

## Quick Start

### Install from PyPI

```bash
pip install foundation-guide
foundation-guide
```

Or install it as a standalone command-line tool:

```bash
uv tool install foundation-guide
foundation-guide
```

### Run from source

Requirements: Python 3.11 or newer and [uv](https://docs.astral.sh/uv/). The game uses only the Python standard library, with no third-party dependencies.

On Windows, double-click:

```text
play.bat
```

Or open a terminal in the project directory:

```powershell
cd foundation-guide
uv run python -m foundation_guide
```

On other platforms:

```bash
uv run python -m foundation_guide
```

### Command-line options

```text
--no-color        disable ANSI colour
--ascii           use ASCII box drawing
--width N         set the text width
--load [name]     load a save (default: autosave)
--script FILE     play commands from a file (testing / demos)
--debug           show full tracebacks on errors
--version         show the version
```

For example:

```powershell
uv run python -m foundation_guide --no-color --width 88
uv run python -m foundation_guide --script tests\walkthrough_full.txt --no-color
```

---

## The Three Acts

| Act | Title | Protagonist | Setting |
|---|---|---|---|
| I | The Psychohistorians | Gaal Dornick | Trantor |
| II | The Mayors | Salvor Hardin | Terminus |
| III | The Mule | Bayta Darell | Kalgan, Trantor, Rossem |

Each act has its own locations, characters, puzzle chain, scoring, and endings. Completing an act moves you automatically to the next one and writes an autosave between acts.

---

## How to Play

The game accepts natural English commands. Articles, capitalisation, and punctuation are mostly ignored, and `IT` / `THEM` refer to the last object mentioned.

### Movement

```text
NORTH / SOUTH / EAST / WEST / UP / DOWN
N / S / E / W / U / D
GO <exit>          ENTER <place>          EXIT
BOARD <ship>
```

### Exploration and objects

```text
LOOK               EXAMINE <object>       READ <object>
SEARCH <object>    TAKE <object>          TAKE ALL
DROP <object>      INVENTORY / I
OPEN / CLOSE <object>
UNLOCK <object> WITH <key>
WEAR / REMOVE <clothing>
PUT <object> IN / ON <container>
```

### Characters and puzzles

```text
TALK TO <character>
ASK <character> ABOUT <topic>
GIVE <object> TO <character>
SHOW <object> TO <character>
USE <object> [ON <object>]
PUSH / PULL / PRESS / TURN / SWITCH <object>
SET <object> TO <value>
TYPE <text>
SAY <words>
```

### Meta commands

```text
GUIDE              list unlocked Guide entries
GUIDE <topic>      read an entry
HINT               a hint for the current puzzle (never costs points)
MAP                show a map of visited locations
SCORE              show score, rank, and statistics
SAVE [name]        save (default: quicksave)
LOAD [name]        load (default: quicksave)
UNDO               undo one turn
RESTART            start over (asks for confirmation)
ACHIEVEMENTS       list achievements
QUIT               leave the game
```

---

## Features

- **A complete three-act campaign**: every act has its own map, puzzle chain, character dialogue, and endings.
- **A forgiving parser**: supports `PICK UP`, `LOOK AT`, `PUT X IN Y`, `USE X ON Y`, `ASK X ABOUT Y`, pronouns, `TAKE ALL`, and direction abbreviations.
- **An unlockable Guide**: 20 comic entries unlocked through exploration, conversation, and story progress. Read them any time with `GUIDE`.
- **Death without dead ends**: dying rewinds one turn and restores the state from before the fatal choice. There are no unrecoverable failures.
- **Hints never cost points**: `HINT` only affects the Guide's opinion of you, never your score.
- **Scoring and ranks**: 100 points per act, 300 in total. Your final score determines your rank and unlocks achievements.
- **Multiple endings**: two political paths in Act II and two final choices in Act III. Every choice is worth full marks, and every choice has consequences.
- **Saves**: JSON format. Source runs keep saves in `saves/`; installed copies use the platform's user-data directory (on Windows, `%LOCALAPPDATA%\foundation-guide\saves`). Override it with `FOUNDATION_GUIDE_SAVE_DIR`. The game autosaves between acts and lets you save at any time.
- **Standard library only**: no third-party dependencies. Clone it and run.

---

## Walkthrough and Tests

The full walkthrough is in **[walkthrough.md](walkthrough.md)**, with recommended routes for all three acts, both endings, and a scoring breakdown. It contains heavy spoilers; play the game once first.

Run the automated tests:

```powershell
uv run python -m unittest discover -s tests -v
```

The current suite covers:

- parser behaviour: directions, compound verbs, articles, pronouns, `USE ... ON ...`, `SET ... TO ...`, and more
- integrity of all three worlds: exits, object placement, NPC placement, and Guide entries
- the 100-point route through Act I
- both Act II endings, "faith" and "trade", at 100 points each
- both Act III endings, the quiet shot and the silence, at 100 points each
- a continuous three-act run at 300 points
- hints not costing points, death rewind, save/load, and Guide lookup

You can also play the full script directly to watch the whole story:

```powershell
uv run python -m foundation_guide --script tests\walkthrough_full.txt --no-color
```

---

## Project Structure

```text
foundation-guide/
├─ foundation_guide/
│  ├─ __main__.py        command-line entry point and menu
│  ├─ engine.py          game loop, command dispatch, scoring, saves
│  ├─ model.py           Room / Object / NPC / Exit / World data model
│  ├─ state.py           serialisable ActState and Meta state
│  ├─ parser.py          forgiving English command parser
│  ├─ ui.py              terminal output, wrapping, colour, script mode
│  ├─ guide.py           20 Guide entries
│  └─ episodes/
│     ├─ act1.py         Act I: The Psychohistorians
│     ├─ act2.py         Act II: The Mayors
│     └─ act3.py         Act III: The Mule
├─ tests/
│  ├─ test_game.py       automated tests
│  ├─ walkthrough_*.txt  act-by-act and full-game scripts
│  └─ run_act.py         single-act debugging runner
├─ saves/                save directory for source runs
├─ pyproject.toml
├─ play.bat
├─ walkthrough.md
└─ README.md
```

---

## Design Notes

The game is data-driven. Each act is a `World` containing rooms, objects, NPCs, and exits. All mutable state lives in `ActState`, so saving, loading, and undo are just serialisation and snapshots. NPC dialogue, puzzle conditions, and scoring events are callbacks attached to the data objects, keeping story logic separate from the engine.

The prose aims for a mixture of the two authors: Asimov's historical scale and political logic, plus Adams' footnotes, bureaucratic absurdity, and a towel that should never be underestimated.

---

## Contributors

- **Tan Long** ([@tanloong](https://github.com/tanloong)) — project author, design, and direction.
- **DeepSeek V4.1 Flash Free** (OpenCode) — AI pair programmer: code, prose, tests, packaging, and documentation.

---

## Credits

- Story and characters from Isaac Asimov's *Foundation* trilogy.
- Comic style inspired by Douglas Adams' *The Hitchhiker's Guide to the Galaxy*.
- A non-commercial fan work, made for learning and entertainment.

So don't panic. Bring a towel. History is watching.
