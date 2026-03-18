"""Core data structures for Tetris 2048 game.

This module provides fundamental classes for representing game state,
including points (coordinates) and tiles (game pieces).
"""

from tetris2048.core.point import Point


# Lazy load Tile to avoid importing heavy rendering dependencies
def __getattr__(name: str) -> object:
    """Lazy load Tile when accessed."""
    if name == "Tile":
        from tetris2048.core.tile import Tile

        return Tile
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
    """Return list of public attributes including lazy-loaded ones."""
    return ["Point", "Tile"]


__all__ = ["Point"]
