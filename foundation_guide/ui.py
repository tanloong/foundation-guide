"""Terminal presentation helpers.

The game deliberately avoids third-party dependencies.  Colour is enabled only
when stdout looks like a terminal, and can be disabled with --no-color.
"""

from __future__ import annotations

import ctypes
import os
import shutil
import sys
import textwrap
from typing import Iterable


RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"


def _enable_windows_ansi() -> bool:
    if os.name != "nt":
        return True
    try:
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        return True
    except Exception:
        return False


def _supports_unicode() -> bool:
    encoding = (getattr(sys.stdout, "encoding", "") or "").lower()
    return "utf" in encoding or encoding in ("utf-8", "utf8")


class UI:
    def __init__(
        self,
        color: bool = True,
        ascii_only: bool = False,
        script: list[str] | None = None,
        width: int | None = None,
    ) -> None:
        self.script = script is not None
        self._script_commands = list(script or [])
        self._script_index = 0
        self.unicode = not ascii_only and _supports_unicode()
        self.color = bool(color) and not self.script
        if self.color:
            self.color = _enable_windows_ansi() and sys.stdout.isatty()
        if width:
            self.width = width
        else:
            try:
                self.width = max(60, min(shutil.get_terminal_size((80, 24)).columns, 96))
            except Exception:
                self.width = 80
        self.width = max(58, self.width - 2)

    # -- styling ---------------------------------------------------------
    def _style(self, code: str, text: str) -> str:
        if not self.color:
            return text
        return f"{code}{text}{RESET}"

    def bold(self, text: str) -> str:
        return self._style(BOLD, text)

    def dim(self, text: str) -> str:
        return self._style(DIM, text)

    def italic(self, text: str) -> str:
        return self._style(ITALIC, text)

    def red(self, text: str) -> str:
        return self._style(RED, text)

    def green(self, text: str) -> str:
        return self._style(GREEN, text)

    def yellow(self, text: str) -> str:
        return self._style(YELLOW, text)

    def blue(self, text: str) -> str:
        return self._style(BLUE, text)

    def magenta(self, text: str) -> str:
        return self._style(MAGENTA, text)

    def cyan(self, text: str) -> str:
        return self._style(CYAN, text)

    def white(self, text: str) -> str:
        return self._style(WHITE, text)

    # -- output ----------------------------------------------------------
    def raw(self, text: str = "") -> None:
        print(text)

    def say(self, text: object = "", end: str = "\n") -> None:
        if text is None:
            return
        string = str(text)
        if not string:
            print(end=end)
            return
        for line in string.split("\n"):
            if not line.strip():
                print(end=end)
                continue
            # Preserve deliberate indentation (footnotes, quoted Guide text).
            if line.startswith("    "):
                indent = "    "
                wrapped = textwrap.fill(
                    line.strip(),
                    width=self.width,
                    initial_indent=indent,
                    subsequent_indent=indent,
                    replace_whitespace=False,
                    drop_whitespace=True,
                )
            else:
                wrapped = textwrap.fill(
                    line,
                    width=self.width,
                    replace_whitespace=False,
                    drop_whitespace=True,
                    break_long_words=True,
                    break_on_hyphens=True,
                )
            print(wrapped, end=end)

    def narrate(self, text: object = "") -> None:
        self.say(text)
        self.say()

    def error(self, text: str) -> None:
        self.say(self.red(text))

    def warning(self, text: str) -> None:
        self.say(self.yellow(text))

    def hint(self, text: str) -> None:
        self.say(self.yellow(text))

    def award(self, text: str) -> None:
        self.say(self.green(text))

    def rule(self, char: str | None = None) -> None:
        if char is None:
            char = "─" if self.unicode else "-"
        print(self.dim(char * self.width))

    def box(self, title: str, body: str, style: str = "cyan") -> None:
        """Print a boxed block, wrapping the body."""
        if not body:
            body = ""
        inner = self.width - 4
        lines: list[str] = []
        for paragraph in str(body).split("\n"):
            if not paragraph.strip():
                lines.append("")
                continue
            lines.extend(
                textwrap.wrap(
                    paragraph,
                    width=inner,
                    replace_whitespace=False,
                    drop_whitespace=True,
                    break_long_words=True,
                )
                or [""]
            )
        title = f" {title} " if title else ""
        if self.unicode:
            top = "┌─" + title + "─" * max(0, self.width - 3 - len(title)) + "┐"
            bottom = "└" + "─" * (self.width - 2) + "┘"
            side = "│"
        else:
            top = "+-" + title + "-" * max(0, self.width - 3 - len(title)) + "+"
            bottom = "+" + "-" * (self.width - 2) + "+"
            side = "|"
        colour = getattr(self, style, self.cyan)
        print(colour(top))
        for line in lines:
            print(colour(side) + " " + line.ljust(inner) + " " + colour(side))
        print(colour(bottom))

    def act_header(self, act_label: str, title: str, subtitle: str, protagonist: str) -> None:
        print()
        self.rule("=")
        self.say(self.bold(act_label.upper()))
        self.say(self.bold(title))
        self.say(self.italic(subtitle))
        self.say()
        self.say(protagonist)
        self.rule("=")
        print()

    def status(self, text: str) -> None:
        self.say(self.dim(text))

    # -- input -----------------------------------------------------------
    def read_command(self) -> str:
        if self.script:
            if self._script_index >= len(self._script_commands):
                raise EOFError
            command = self._script_commands[self._script_index]
            self._script_index += 1
            print(self.green("> ") + command)
            return command
        try:
            return input(self.green("> "))
        except EOFError:
            raise

    def pause(self, prompt: str = "Press ENTER to continue...") -> None:
        if self.script:
            return
        try:
            input(self.dim(prompt))
        except EOFError:
            pass

    def title(self) -> None:
        print()
        self.box(
            "THE HITCHHIKER'S GUIDE TO THE FOUNDATION",
            "A text adventure in three probability spikes.\n\n"
            "An unauthorised psychohistorical simulation, mostly harmless.",
            style="cyan",
        )
        self.say()
        self.say(self.dim("  Based on the Foundation trilogy by Isaac Asimov."))
        self.say(self.dim("  Fan work. Not affiliated with the estate or the Second Foundation."))
        self.say()

    def menu(self, has_save: bool) -> str:
        self.title()
        self.say(self.bold("  What would you like to do?"))
        self.say("   1. Begin a new game")
        if has_save:
            self.say("   2. Continue from the autosave")
        self.say("   3. Read the manual")
        self.say("   4. Quit")
        while True:
            try:
                choice = input(self.green("  > ")).strip().lower()
            except EOFError:
                return "quit"
            if choice in ("1", "new", "n"):
                return "new"
            if choice in ("2", "load", "l", "continue") and has_save:
                return "load"
            if choice in ("3", "help", "h", "manual"):
                return "help"
            if choice in ("4", "quit", "q"):
                return "quit"
            self.error("  The Guide suggests 1, 2, 3, or 4.")


def join_names(names: Iterable[str]) -> str:
    items = [n for n in names if n]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + ", and " + items[-1]
