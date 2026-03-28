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
		...

	def get_min_bounded_tile_matrix(self) -> tuple[np.ndarray, Point | None]:
		"""Get the minimum bounded matrix of tiles and its top-left point."""
		...


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

	def __init__(self, grid_h: int, grid_w: int, ui_panel_units: int = 0) -> None:
		"""Initialize the game grid with given dimensions.

		Args:
			grid_h: The height of the grid in cells.
			grid_w: The width of the grid in cells.
			ui_panel_units: The number of units reserved for the UI panel.
		"""
		color_class = Color
		self.grid_height: int = grid_h
		self.grid_width: int = grid_w
		self.ui_panel_units: int = ui_panel_units
		# Create a tile matrix to store tiles locked on the game grid
		self.tile_matrix: np.ndarray = np.full((grid_h, grid_w), None)
		# The tetromino currently being moved
		self.current_tetromino: DrawableTetromino | None = None
		# Game over flag
		self.game_over: bool = False
		# UI state
		self.score: int = 0
		self.next_tetromino: DrawableTetromino | None = None
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
		# Draw UI panel
		self.draw_ui()
		# Show with 300ms pause
		stddraw.show(300)

	def draw_ui(self) -> None:
		"""Draw the right-side UI panel (score and next tetromino preview)."""
		if self.ui_panel_units <= 0:
			return

		# UI rectangle bounds
		ui_left_x = float(self.grid_width) - 0.5
		ui_bottom_y = -0.5
		ui_w = float(self.ui_panel_units)
		ui_h = float(self.grid_height)

		# Background for UI
		ui_bg = Color(30, 50, 80)
		stddraw.setPenColor(ui_bg)
		stddraw.filledRectangle(ui_left_x, ui_bottom_y, ui_w, ui_h)

		# Draw score at the top of the UI
		stddraw.setPenColor(Color(255, 255, 255))
		stddraw.setFontFamily("Arial")
		stddraw.setFontSize(25)
		score_x = ui_left_x + ui_w / 2
		score_y = ui_bottom_y + ui_h - 1.0  # 1 user-unit down from top
		stddraw.boldText(score_x, score_y, "SCORE")
		stddraw.boldText(score_x, score_y - 1.0, f"{self.score}")

		# Check if there is a next piece to draw
		if self.next_tetromino is None:
			return

		# Get a bounded copy of the next piece tile matrix
		tiles, _ = self.next_tetromino.get_min_bounded_tile_matrix()
		n_rows, n_cols = tiles.shape

		# Compute preview center near the bottom
		vpad_bottom = 0.5
		preview_height = n_rows
		preview_center_y = ui_bottom_y + vpad_bottom + (preview_height / 2)
		preview_center_x = ui_left_x + ui_w / 2

		# Draw "NEXT" text anchored dynamically above the preview piece
		stddraw.setFontSize(25)
		text_y_position = preview_center_y + (preview_height / 2) + 1.0
		stddraw.boldText(score_x, text_y_position, "NEXT")

		# Compute rendering offset for the tiles
		offset_x = preview_center_x - (n_cols / 2)
		offset_y = preview_center_y - (n_rows / 2)

		# Draw the next piece tiles
		for r in range(n_rows):
			for c in range(n_cols):
				t = tiles[r][c]
				if t is None:
					continue
				px = offset_x + c + 0.5
				py = offset_y + (n_rows - 1 - r) + 0.5
				p = Point(px, py)
				t.draw(p, length=1)

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
			True if the cell contains a tile. Returns False for empty
			cells and for positions outside the grid.
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

	def clear_full_rows(self) -> int:
		"""Detect and remove any full rows.

		Returns:
			The total points gained from removed rows (sum of tile numbers).

		Behavior:
		- Collect all non-full rows in bottom-to-top order.
		- Sum numbers for full rows and drop them.
		- Construct a new tile_matrix with the remaining rows at the bottom
		and empty rows at the top.
		"""
		total_points = 0
		remaining_rows: list[np.ndarray] = []

		# Iterate from bottom
		for row in range(self.grid_height):
			row_tiles = self.tile_matrix[row]
			# Determine if row is full
			if any(t is None for t in row_tiles):
				remaining_rows.append(row_tiles.copy())
			else:
				row_sum = 0
				for t in row_tiles:
					if t is not None:
						row_sum += getattr(t, "number", 0)
				total_points += row_sum

		# If no rows were cleared, nothing to do
		if len(remaining_rows) == self.grid_height:
			return 0

		# Build a new tile matrix
		new_matrix = np.full((self.grid_height, self.grid_width), None)
		for i, rtiles in enumerate(remaining_rows):
			new_matrix[i, :] = rtiles

		# Replace the tile matrix
		self.tile_matrix = new_matrix
		return total_points

	def merge_vertical(self) -> int:
		"""Merge vertically adjacent tiles and compress columns (gravity).

		Returns:
			The total points gained by merges (sum of merged tile values).
		"""
		total_points = 0

		for column_index in range(self.grid_width):
			# Extract all non-empty tiles in this column
			current_column_tiles = []
			for row_index in range(self.grid_height):
				tile = self.tile_matrix[row_index][column_index]
				if tile is not None:
					current_column_tiles.append(tile)

			# Merge adjacent tiles with the same number
			merged_column_tiles = []
			index = 0
			while index < len(current_column_tiles):
				lower_tile = current_column_tiles[index]

				# Check if there is a tile above it and
				# if their numbers match
				if index < len(current_column_tiles) - 1:
					upper_tile = current_column_tiles[index + 1]

					if getattr(
						lower_tile, "number", None
					) == getattr(upper_tile, "number", None):
						# Merge happens!
						new_value = lower_tile.number * 2
						lower_tile.set_number(new_value)
						total_points += new_value
						merged_column_tiles.append(lower_tile)
						index += 2  # Skip the upper tile
						continue

				# No merge, just keep the tile
				merged_column_tiles.append(lower_tile)
				index += 1

			# Write the compacted/merged tiles back to the grid
			for row_index in range(self.grid_height):
				if row_index < len(merged_column_tiles):
					self.tile_matrix[row_index][column_index] = (
						merged_column_tiles[row_index]
					)
				else:
					self.tile_matrix[row_index][column_index] = None

		return total_points

	def remove_floating_components(self) -> int:
		"""Remove connected components that do not touch the bottom row."""
		total_points = 0
		anchored_positions = set()
		coordinates_to_check_queue = []

		# Add all tiles on the bottom row
		for column_index in range(self.grid_width):
			if self.tile_matrix[0][column_index] is not None:
				coordinates_to_check_queue.append((0, column_index))
				anchored_positions.add((0, column_index))

		# Find all tiles connected to the anchored set
		adjacent_coordinate_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
		while coordinates_to_check_queue:
			current_row_index, current_column_index = (
				coordinates_to_check_queue.pop(0)
			)
			for row_offset, column_offset in adjacent_coordinate_offsets:
				neighbor_row_index = current_row_index + row_offset
				neighbor_column_index = (
					current_column_index + column_offset
				)

				if (
					0 <= neighbor_row_index < self.grid_height
					and 0 <= neighbor_column_index < self.grid_width
				):
					is_not_anchored = (
						neighbor_row_index,
						neighbor_column_index,
					) not in anchored_positions
					has_tile = (
						self.tile_matrix[neighbor_row_index][
							neighbor_column_index
						]
						is not None
					)

					if is_not_anchored and has_tile:
						anchored_positions.add(
							(
								neighbor_row_index,
								neighbor_column_index,
							)
						)
						coordinates_to_check_queue.append(
							(
								neighbor_row_index,
								neighbor_column_index,
							)
						)

		# Remove tiles not in the anchored set and add their points
		for row_index in range(self.grid_height):
			for column_index in range(self.grid_width):
				current_tile = self.tile_matrix[row_index][column_index]
				if (
					current_tile is not None
					and (row_index, column_index)
					not in anchored_positions
				):
					total_points += getattr(
						current_tile, "number", 0
					)
					self.tile_matrix[row_index][column_index] = None

		return total_points

	def _run_stabilization_loop(self) -> int:
		"""Run merge/clear/remove passes until no changes; return points gained.

		Encapsulates the repeated-pass loop so update_grid remains small.
		"""
		total_points_accumulated = 0
		while True:
			merged_points = self.merge_vertical()
			cleared_points = self.clear_full_rows()
			removed_points = self.remove_floating_components()
			if (
				merged_points == 0
				and cleared_points == 0
				and removed_points == 0
			):
				break
			total_points_accumulated += (
				merged_points + cleared_points + removed_points
			)
		return total_points_accumulated

	def update_grid(self, tiles_to_lock: np.ndarray, blc_position: Point) -> bool:
		"""Lock tiles onto the grid after a tetromino lands.

		After locking, repeatedly perform vertical merges, row clears, and
		floating-component removals until the board stabilizes. Note that
		gravity / column compression is applied implicitly by merges and row
		clears: merged tiles are written back toward the bottom, and cleared
		rows are removed and remaining rows are compacted. Floating-component
		removal only removes disconnected tiles and does NOT perform a gravity
		pass (empty cells remain until another operation compacts them).
		"""
		self.current_tetromino = None

		n_rows, n_cols = cast("tuple[int, int]", tiles_to_lock.shape)

		# Lock incoming tiles into the persistent tile matrix
		for local_col in range(n_cols):
			for local_row in range(n_rows):
				incoming = tiles_to_lock[local_row][local_col]
				if incoming is None:
					continue

				target = Point()
				target.x = blc_position.x + local_col
				target.y = blc_position.y + (n_rows - 1) - local_row

				if self.is_inside(target.y, target.x):
					self.tile_matrix[target.y][target.x] = incoming
				else:
					# Tile landed above visible grid -> game over
					self.game_over = True

		# Run stabilization loop and collect points.
		total_points_accumulated = self._run_stabilization_loop()

		# Add any accumulated points once
		if total_points_accumulated:
			self.score = (
				getattr(self, "score", 0) + total_points_accumulated
			)

		return self.game_over
