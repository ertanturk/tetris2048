"""Tetris 2048 - A hybrid game combining Tetris and 2048 mechanics.

This package provides the main game implementation with support for
playing tetrominoes (Tetris pieces) on a grid with 2048 merge mechanics.
"""

__version__ = "0.0.0"
__author__ = "Ertan Tunç Türk"
__email__ = "turke@mef.edu.tr"


# Lazy imports to avoid loading heavy dependencies until needed
def __getattr__(name: str) -> object:
	"""Lazy load GameEngine when accessed."""
	if name == "GameEngine":
		from tetris2048.game import GameEngine  # noqa: PLC0415

		return GameEngine
	msg = f"module '{__name__}' has no attribute '{name}'"
	raise AttributeError(msg)


def __dir__() -> list[str]:
	"""Return list of public attributes including lazy-loaded ones."""
	return ["GameEngine"]


__all__: list[str] = []
