"""Data model for rooms, objects, NPCs, exits, and episodes.

The model is deliberately small and data-driven.  Episode modules fill in
dataclasses; the engine owns all mutable state so that save files and undo are
just snapshots of one ActState.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:  # pragma: no cover - only for type checkers
    from .engine import Game

Text = str | Callable[["Game"], str]
Handler = Callable[..., bool | None]


@dataclass
class Exit:
    """A connection from one room to another.

    ``condition`` may be used for locked doors.  ``on_use`` runs before the
    move and can print its own message; returning a truthy value cancels the
    move.
    """

    dest: str
    condition: Callable[["Game"], bool] | None = None
    blocked: str = "You can't go that way."
    hidden: bool = False
    label: str | None = None
    on_use: Handler | None = None


@dataclass
class Room:
    key: str
    name: str
    desc: Text
    brief: Text | None = None
    exits: dict[str, Exit] = field(default_factory=dict)
    extras: dict[str, str] = field(default_factory=dict)
    coords: tuple[int, int] = (0, 0)
    map_label: str | None = None
    on_enter: Callable[["Game", bool], bool | None] | None = None
    dark: bool = False


@dataclass
class Object:
    key: str
    names: list[str]
    desc: Text
    short: str | None = None
    location: str | None = None
    takeable: bool = True
    fixed: bool = False
    container: bool = False
    open: bool = True
    locked: bool = False
    unlock_key: str | None = None
    transparent: bool = False
    readable: Text | None = None
    wearable: bool = False
    hidden: bool = False
    listed: bool = True
    surface: bool = False
    openable: bool = False
    on_take: Callable[["Game", "Object"], bool | None] | None = None
    on_drop: Callable[["Game", "Object"], bool | None] | None = None
    on_open: Callable[["Game", "Object"], bool | None] | None = None
    on_close: Callable[["Game", "Object"], bool | None] | None = None
    on_read: Callable[["Game", "Object"], bool | None] | None = None
    on_use: Callable[["Game", "Object", Any], bool | None] | None = None
    on_use_with: Callable[["Game", "Object", Any], bool | None] | None = None
    on_receive: Callable[["Game", "Object", "Object"], bool | None] | None = None
    on_search: Callable[["Game", "Object"], bool | None] | None = None
    on_push: Callable[["Game", "Object"], bool | None] | None = None
    on_pull: Callable[["Game", "Object"], bool | None] | None = None
    on_switch: Callable[["Game", "Object"], bool | None] | None = None
    on_switch_on: Callable[["Game", "Object"], bool | None] | None = None
    on_switch_off: Callable[["Game", "Object"], bool | None] | None = None
    on_set: Callable[["Game", "Object", str], bool | None] | None = None
    on_press: Callable[["Game", "Object"], bool | None] | None = None
    on_throw: Callable[["Game", "Object", Any], bool | None] | None = None

    def display_name(self) -> str:
        return self.short or (self.names[0] if self.names else self.key)


@dataclass
class NPC:
    key: str
    names: list[str]
    desc: Text
    short: str | None = None
    location: str | None = None
    topics: dict[str, Any] = field(default_factory=dict)
    default: Text = "They have nothing to say about that."
    on_talk: Callable[["Game", "NPC"], bool | None] | None = None
    on_ask: Callable[["Game", "NPC", str], bool | None] | None = None
    on_give: Callable[["Game", "NPC", Object], bool | None] | None = None
    on_show: Callable[["Game", "NPC", Object], bool | None] | None = None
    on_say: Callable[["Game", "NPC", str], bool | None] | None = None
    on_attack: Callable[["Game", "NPC"], bool | None] | None = None
    listed: bool = True

    def display_name(self) -> str:
        return self.short or (self.names[0] if self.names else self.key)


@dataclass
class World:
    act: int
    title: str
    subtitle: str
    protagonist: str
    start_room: str
    intro: Text
    rooms: dict[str, Room]
    objects: dict[str, Object]
    npcs: dict[str, NPC]
    max_score: int
    guide_keys: list[str] = field(default_factory=list)
    hints: Callable[["Game"], str] | None = None
    on_start: Callable[["Game"], None] | None = None
    on_turn: Callable[["Game"], None] | None = None
    on_enter: Callable[["Game", str], None] | None = None
    on_say: Callable[["Game", str], bool | None] | None = None
    on_type: Callable[["Game", str], bool | None] | None = None
    on_command: Callable[["Game", str, Any], bool | None] | None = None
    epilogue: Text | None = None
    ending_title: str = "THE END"

    def room(self, key: str) -> Room:
        return self.rooms[key]

    def obj(self, key: str) -> Object:
        return self.objects[key]

    def npc(self, key: str) -> NPC:
        return self.npcs[key]
