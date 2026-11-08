"""Episode registry."""

from __future__ import annotations

from ..model import World

EPISODE_COUNT = 3


def load_episode(index: int) -> World:
    if index == 0:
        from . import act1

        return act1.build()
    if index == 1:
        from . import act2

        return act2.build()
    if index == 2:
        from . import act3

        return act3.build()
    raise IndexError(f"No episode {index}")
