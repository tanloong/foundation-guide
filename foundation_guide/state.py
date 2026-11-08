"""Mutable game state and serialisation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ActState:
    room: str = ""
    score: int = 0
    moves: int = 0
    flags: set[str] = field(default_factory=set)
    counters: dict[str, int] = field(default_factory=dict)
    obj_loc: dict[str, str | None] = field(default_factory=dict)
    obj_open: dict[str, bool] = field(default_factory=dict)
    obj_locked: dict[str, bool] = field(default_factory=dict)
    obj_worn: set[str] = field(default_factory=set)
    seen: set[str] = field(default_factory=set)
    finished: bool = False
    pronoun: str | None = None
    verbose: bool = True
    hint_count: int = 0
    pending: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "room": self.room,
            "score": self.score,
            "moves": self.moves,
            "flags": sorted(self.flags),
            "counters": dict(self.counters),
            "obj_loc": dict(self.obj_loc),
            "obj_open": dict(self.obj_open),
            "obj_locked": dict(self.obj_locked),
            "obj_worn": sorted(self.obj_worn),
            "seen": sorted(self.seen),
            "finished": self.finished,
            "pronoun": self.pronoun,
            "verbose": self.verbose,
            "hint_count": self.hint_count,
            "pending": self.pending,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActState":
        return cls(
            room=data.get("room", ""),
            score=int(data.get("score", 0)),
            moves=int(data.get("moves", 0)),
            flags=set(data.get("flags", [])),
            counters={k: int(v) for k, v in data.get("counters", {}).items()},
            obj_loc=dict(data.get("obj_loc", {})),
            obj_open={k: bool(v) for k, v in data.get("obj_open", {}).items()},
            obj_locked={k: bool(v) for k, v in data.get("obj_locked", {}).items()},
            obj_worn=set(data.get("obj_worn", [])),
            seen=set(data.get("seen", [])),
            finished=bool(data.get("finished", False)),
            pronoun=data.get("pronoun"),
            verbose=bool(data.get("verbose", True)),
            hint_count=int(data.get("hint_count", 0)),
            pending=data.get("pending"),
        )


@dataclass
class Meta:
    act_scores: dict[int, int] = field(default_factory=dict)
    guide_unlocked: set[str] = field(default_factory=set)
    deaths: int = 0
    hints: int = 0
    achievements: set[str] = field(default_factory=set)
    doctrine: str = "faith"
    ending: str | None = None
    started_at: float = 0.0

    @property
    def total_score(self) -> int:
        return sum(self.act_scores.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "act_scores": {str(k): v for k, v in self.act_scores.items()},
            "guide_unlocked": sorted(self.guide_unlocked),
            "deaths": self.deaths,
            "hints": self.hints,
            "achievements": sorted(self.achievements),
            "doctrine": self.doctrine,
            "ending": self.ending,
            "started_at": self.started_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Meta":
        return cls(
            act_scores={int(k): int(v) for k, v in data.get("act_scores", {}).items()},
            guide_unlocked=set(data.get("guide_unlocked", [])),
            deaths=int(data.get("deaths", 0)),
            hints=int(data.get("hints", 0)),
            achievements=set(data.get("achievements", [])),
            doctrine=data.get("doctrine", "faith"),
            ending=data.get("ending"),
            started_at=float(data.get("started_at", 0.0)),
        )
