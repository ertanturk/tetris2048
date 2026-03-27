"""Rendering utilities for Tetris 2048.

This module provides all display and graphics functionality including colors,
shapes, text, and images.
"""

import importlib


def __getattr__(name: str) -> object:
	"""Lazy load heavy dependencies (pygame-based modules).

	Args:
		name: The attribute name being requested.

	Returns:
		The requested module or symbol.

	Raises:
		AttributeError: If the attribute doesn't exist.
	"""
	if name == "Color":
		from tetris2048.rendering.color import Color  # noqa: PLC0415

		return Color
	if name == "Picture":
		from tetris2048.rendering.picture import Picture  # noqa: PLC0415

		return Picture
	if name == "stddraw":
		return importlib.import_module(
			".stddraw", package="tetris2048.rendering"
		)
	msg = f"module '{__name__}' has no attribute '{name}'"
	raise AttributeError(msg)


def __dir__() -> list[str]:
	"""Return list of public attributes including lazy-loaded ones."""
	return ["Color", "Picture", "stddraw"]


__all__: list[str] = []
