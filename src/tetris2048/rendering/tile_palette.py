"""Tile color palette for 2048 game tiles."""

from __future__ import annotations

import math

from tetris2048.rendering.color import Color

PALETTE: dict[int, tuple[Color, Color, Color]] = {
	2: (Color(238, 228, 218), Color(119, 110, 101), Color(187, 173, 160)),
	4: (Color(237, 224, 200), Color(119, 110, 101), Color(187, 173, 160)),
	8: (Color(242, 177, 121), Color(255, 255, 255), Color(205, 133, 63)),
	16: (Color(245, 149, 99), Color(255, 255, 255), Color(200, 100, 40)),
	32: (Color(246, 124, 95), Color(255, 255, 255), Color(180, 80, 30)),
	64: (Color(246, 94, 59), Color(255, 255, 255), Color(150, 60, 30)),
	128: (Color(237, 207, 114), Color(255, 255, 255), Color(140, 110, 50)),
	256: (Color(237, 204, 97), Color(255, 255, 255), Color(130, 100, 50)),
	512: (Color(237, 200, 80), Color(255, 255, 255), Color(120, 90, 40)),
	1024: (Color(237, 197, 63), Color(255, 255, 255), Color(110, 80, 30)),
	2048: (Color(237, 194, 46), Color(255, 255, 255), Color(90, 60, 30)),
}

# Fallback colors used when a number isn't listed in PALETTE.
_DEFAULT_BG = Color(60, 58, 50)
_DEFAULT_FG = Color(255, 255, 255)
_DEFAULT_BOX = Color(120, 110, 100)


def get_tile_colors(number: int) -> tuple[Color, Color, Color]:
	"""Return (background, foreground, box) Colors for a given tile number.

	Behavior:
	- If `number` is present in PALETTE, return that triple.
	- If `number` is a positive integer not in PALETTE, compute a sensible
	fallback color by darkening a base color according to log2(number).
	- For any invalid `number` input (non-integer, <= 0), return default colors.
	"""
	# Exact match in palette
	colors = PALETTE.get(number)
	if colors is not None:
		return colors

	# Validate number must be a positive integer
	if not isinstance(number, int) or number <= 0:
		return _DEFAULT_BG, _DEFAULT_FG, _DEFAULT_BOX

	# Compute magnitude-based factor using log
	k = max(0, int(math.log2(number)) - 1)

	# Clamp intensity so colors don't become too dark
	factor = min(8, k)

	# Base RGB values
	base_r, base_g, base_b = 120, 110, 100

	# Darken proportional to factor
	r = max(30, base_r - factor * 10)
	g = max(30, base_g - factor * 8)
	b = max(30, base_b - factor * 6)

	bg = Color(r, g, b)
	fg = _DEFAULT_FG
	box = Color(max(0, r - 30), max(0, g - 20), max(0, b - 10))

	return bg, fg, box


def set_palette(new_palette: dict[int, tuple[Color, Color, Color]]) -> None:
	"""Replace the current palette with `new_palette`.

	Validates input and updates the existing PALETTE dict in-place (no rebinding).
	Raises ValueError on invalid input.
	"""
	# Basic validation
	if not isinstance(new_palette, dict):
		error_msg = "new_palette must be a dict[int, (Color,Color,Color)]"
		raise TypeError(error_msg)

	# Validate keys and values
	for k, v in new_palette.items():
		tuple_colors: int = 3
		if not isinstance(k, int) or k <= 0:
			error_msg = (
				"palette keys must be positive integers (tile numbers)"
			)
			raise ValueError(error_msg)
		if (
			not isinstance(v, tuple)
			or len(v) != tuple_colors
			or not all(isinstance(x, Color) for x in v)
		):
			error_msg = (
				"palette values must be tuples of three Color instances"
			)
			raise ValueError(error_msg)

	PALETTE.clear()
	PALETTE.update(new_palette)
