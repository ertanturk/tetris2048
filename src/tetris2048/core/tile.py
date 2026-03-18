"""Tile class for representing numbered tiles in the game.

A Tile represents a 2048-style numbered tile that appears in the game,
with a number value, background color, and foreground color.
"""

from typing import TYPE_CHECKING, Any

from tetris2048.core.point import Point

if TYPE_CHECKING:
    pass


_cached_color: Any = None
_cached_stddraw: Any = None


def _lazy_import_color() -> Any:
    """Lazily import Color to avoid circular imports."""
    global _cached_color
    if _cached_color is None:
        from tetris2048.rendering.color import Color as _Color

        _cached_color = _Color
    return _cached_color


def _lazy_import_stddraw() -> Any:
    """Lazily import stddraw to avoid circular imports."""
    global _cached_stddraw
    if _cached_stddraw is None:
        from tetris2048.rendering import stddraw as _stddraw

        _cached_stddraw = _stddraw
    return _cached_stddraw


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

    def __init__(self) -> None:
        """Initialize a tile with number 2 and default colors."""
        ColorClass = _lazy_import_color()
        self.number: int = 2
        self.background_color = ColorClass(151, 178, 199)
        self.foreground_color = ColorClass(0, 100, 200)
        self.box_color = ColorClass(0, 100, 200)

    def draw(self, position: Point, length: float = 1) -> None:
        """Draw this tile at the given position.

        Args:
            position: The center position where to draw the tile.
            length: The size of the tile. Defaults to 1.
        """
        stddraw = _lazy_import_stddraw()
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

    def __str__(self) -> str:
        """Return the string representation of this tile.

        Returns:
            A string showing the tile's number.
        """
        return str(self.number)

    def __repr__(self) -> str:
        """Return the representation of this tile.

        Returns:
            A string representation suitable for debugging.
        """
        return f"Tile(number={self.number})"
