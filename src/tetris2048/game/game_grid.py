"""Game grid class for managing the game board state.

The GameGrid represents the playing field and manages the placement
of tiles, collision detection, and game over conditions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

import numpy as np

from tetris2048.core.point import Point
from tetris2048.rendering import stddraw
from tetris2048.rendering.color import Color

if TYPE_CHECKING:
	from tetris2048.core.tile import Tile


class DrawableTetromino(Protocol):
	"""Protocol for tetromino-like objects that can be drawn."""

	def draw(self) -> None:
		"""Draw the tetromino on the screen."""


class GameGrid:
	"""Represents the game grid for Tetris 2048.

	The grid manages the placement of tiles, tracks the current tetromino,
	and handles drawing the game state to the display.

	Attributes:
	grid_height (int): The height of the grid in cells.
		grid_width (int): The width of the grid in cells.
		tile_matrix (np.ndarray): 2D matrix storing tiles or None for
			empty cells.
		current_tetromino (Optional): The currently active tetromino.
		game_over (bool): Whether the game has ended.
	"""

	def __init__(self, grid_h: int, grid_w: int) -> None:
		"""Initialize the game grid with given dimensions.

		Args:
			grid_h: The height of the grid in cells.
			grid_w: The width of the grid in cells.
		"""
		color_class = Color
		self.grid_height: int = grid_h
		self.grid_width: int = grid_w
		# Create a tile matrix to store tiles locked on the game grid
		self.tile_matrix: np.ndarray = np.full((grid_h, grid_w), None)
		# The tetromino currently being moved
		self.current_tetromino: DrawableTetromino | None = None
		# Game over flag
		self.game_over: bool = False
		# Colors for display
		self.empty_cell_color: Color = color_class(42, 69, 99)
		self.line_color: Color = color_class(0, 100, 200)
		self.boundary_color: Color = color_class(0, 100, 200)
		# Thickness values for drawing
		self.line_thickness: float = 0.002
		self.box_thickness: float = 5 * self.line_thickness

	def display(self) -> None:
		"""Display the game grid on the screen.

		Clears the background, draws the grid, current tetromino,
		and boundary box, then shows the result.
		"""
		# Clear background
		stddraw.clear(self.empty_cell_color)
		# Draw the grid
		self.draw_grid()
		# Draw the current tetromino if it exists
		if self.current_tetromino is not None:
			self.current_tetromino.draw()
		# Draw boundary box
		self.draw_boundaries()
		# Show with 500ms pause
		stddraw.show(500)

	def draw_grid(self) -> None:
		"""Draw the game grid cells and lines.

		Draws all tiles in the grid and the lines separating cells.
		"""
		# Draw each tile in the grid
		for row in range(self.grid_height):
			for col in range(self.grid_width):
				tile = cast("Tile | None", self.tile_matrix[row][col])
				if tile is not None:
					tile.draw(Point(col, row))

		# Draw inner grid lines
		stddraw.setPenColor(self.line_color)
		stddraw.setPenRadius(self.line_thickness)

		start_x, end_x = -0.5, self.grid_width - 0.5
		start_y, end_y = -0.5, self.grid_height - 0.5

		# Vertical lines
		for x in np.arange(start_x + 1, end_x, 1):
			stddraw.line(x, start_y, x, end_y)

		# Horizontal lines
		for y in np.arange(start_y + 1, end_y, 1):
			stddraw.line(start_x, y, end_x, y)

		stddraw.setPenRadius()  # Reset pen radius

	def draw_boundaries(self) -> None:
		"""Draw the boundary box around the game grid."""
		stddraw.setPenColor(self.boundary_color)
		stddraw.setPenRadius(self.box_thickness)

		pos_x, pos_y = -0.5, -0.5
		stddraw.rectangle(pos_x, pos_y, self.grid_width, self.grid_height)

		stddraw.setPenRadius()  # Reset pen radius

	def is_occupied(self, row: int, col: int) -> bool:
		"""Check if a grid cell is occupied by a tile.

		Args:
			row: The row index of the cell.
			col: The column index of the cell.

		Returns:
			True if the cell is occupied or outside the grid, False
			otherwise.
		"""
		if not self.is_inside(row, col):
			return False
		return self.tile_matrix[row][col] is not None

	def is_inside(self, row: int, col: int) -> bool:
		"""Check if a position is within the game grid bounds.

		Args:
			row: The row index to check.
			col: The column index to check.

		Returns:
			True if the position is inside the grid, False otherwise.
		"""
		return 0 <= row < self.grid_height and 0 <= col < self.grid_width

	def update_grid(self, tiles_to_lock: np.ndarray, blc_position: Point) -> bool:
		"""Lock tiles onto the grid after a tetromino lands.

		Args:
			tiles_to_lock: The tile matrix of the landed tetromino.
			blc_position: The bottom-left corner position of the tiles.

		Returns:
			True if the game is over, False otherwise.
		"""
		self.current_tetromino = None

		n_rows, n_cols = cast("tuple[int, int]", tiles_to_lock.shape)

		for col in range(n_cols):
			for row in range(n_rows):
				if tiles_to_lock[row][col] is not None:
					# Calculate position on game grid
					pos = Point()
					pos.x = blc_position.x + col
					pos.y = blc_position.y + (n_rows - 1) - row

					if self.is_inside(pos.y, pos.x):
						self.tile_matrix[pos.y][pos.x] = (
							tiles_to_lock[row][col]
						)
					else:
						# Game over if tile is above grid
						self.game_over = True

		return self.game_over
