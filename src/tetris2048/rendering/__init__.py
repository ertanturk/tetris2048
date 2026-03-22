"""Rendering utilities for Tetris 2048.

This module provides all display and graphics functionality including colors,
shapes, text, and images.
"""

import importlib

from tetris2048.rendering.color import Color


def __getattr__(name: str) -> object:
	"""Lazy load heavy dependencies (pygame-based modules).

	Args:
	    name: The attribute name being requested.

	Returns:
	    The requested module or symbol.

	Raises:
	    AttributeError: If the attribute doesn't exist.
	"""
	if name == "Picture":
		from tetris2048.rendering.picture import Picture

		return Picture
	if name == "stddraw":
		return importlib.import_module(
			".stddraw", package="tetris2048.rendering"
		)
	raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:
	"""Return list of public attributes including lazy-loaded ones."""
	return ["Color", "Picture", "stddraw"]


__all__ = ["Color"]
