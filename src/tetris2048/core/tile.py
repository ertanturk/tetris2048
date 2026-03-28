"""Tile class for representing numbered tiles in the game.

A Tile represents a 2048-style numbered tile that appears in the game,
with a number value, background color, and foreground color.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from tetris2048.rendering import stddraw
from tetris2048.rendering.color import Color
from tetris2048.rendering.tile_palette import get_tile_colors

if TYPE_CHECKING:
	from tetris2048.core.point import Point


def _lazy_import_color() -> type[Color]:
	"""Return the `Color` class (top-level import).

	Kept as a function for API compatibility with earlier lazy loader.
	"""
	return Color


# `stddraw` is imported at module level and used at runtime.
# We avoid using a module object as a type in annotations.


class Tile:
	"""Represents a numbered tile as in 2048 game.

	Attributes:
		number (int): The number displayed on this tile.
		background_color: The background color of the tile.
		foreground_color: The color of the number text.
		box_color: The color of the tile border.
	"""

	# Class variables shared among all Tile objects
	boundary_thickness: float = 0.004
	font_family: str = "Arial"
	font_size: int = 16

	def __init__(self, number: int = 2) -> None:
		"""Initialize a tile with number 2 and default colors."""
		self.number: int = number
		bg, fg, box = get_tile_colors(self.number)
		self.background_color: Color = bg
		self.foreground_color: Color = fg
		self.box_color: Color = box

	def set_number(self: Tile, new_number: int) -> None:
		"""Update this tile's numeric value and refresh its colors.

		Call this after merging to update the tile appearance.
		"""
		self.number = new_number
		bg, fg, box = get_tile_colors(self.number)
		self.background_color = bg
		self.foreground_color = fg
		self.box_color = box

	def draw(self, position: Point, length: float = 1) -> None:
		"""Draw this tile at the given position.

		Args:
			position: The center position where to draw the tile.
			length: The size of the tile. Defaults to 1.
		"""
		# Draw the tile as a filled square
		stddraw.setPenColor(self.background_color)
		stddraw.filledSquare(position.x, position.y, length / 2)

		# Draw the bounding box around the tile
		stddraw.setPenColor(self.box_color)
		stddraw.setPenRadius(Tile.boundary_thickness)
		stddraw.square(position.x, position.y, length / 2)
		stddraw.setPenRadius()

		# Draw the number on the tile
		stddraw.setPenColor(self.foreground_color)
		stddraw.setFontFamily(Tile.font_family)
		stddraw.setFontSize(Tile.font_size)
		stddraw.boldText(position.x, position.y, str(self.number))

	@override
	def __str__(self) -> str:
		"""Return the string representation of this tile.

		Returns:
			A string showing the tile's number.
		"""
		return str(self.number)

	@override
	def __repr__(self) -> str:
		"""Return the representation of this tile.

		Returns:
			A string representation suitable for debugging.
		"""
		return f"Tile(number={self.number})"
