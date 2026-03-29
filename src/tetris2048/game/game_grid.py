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

WIN_CONDITION = 2048


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
		# Win state flags
		self.game_won: bool = False
		self.kept_playing: bool = False
		# UI state
		self.score: int = 0
		self.next_tetromino: DrawableTetromino | None = None
		self.held_tetromino: DrawableTetromino | None = None
		# Colors for display
		self.empty_cell_color: Color = color_class(42, 69, 99)
		self.line_color: Color = color_class(0, 100, 200)
		self.boundary_color: Color = color_class(0, 100, 200)
		# Thickness values for drawing
		self.line_thickness: float = 0.002
		self.box_thickness: float = 5 * self.line_thickness

	def display(self, pause: int = 500) -> None:
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
		# Show with pause default is 500ms
		stddraw.show(pause)

	def draw_ui(self) -> None:
		"""Draw the right-side UI panel (score, hold, and next preview)."""
		if self.ui_panel_units <= 0:
			return

		ui_left_x = float(self.grid_width) - 0.5
		ui_bottom_y = -0.5
		ui_w = float(self.ui_panel_units)
		ui_h = float(self.grid_height)

		# 1. UI Background & Divider Line
		stddraw.setPenColor(Color(40, 44, 52))  # Dark slate background
		stddraw.filledRectangle(ui_left_x, ui_bottom_y, ui_w, ui_h)

		stddraw.setPenColor(Color(80, 84, 92))  # Subtle divider line
		stddraw.line(ui_left_x, ui_bottom_y, ui_left_x, ui_bottom_y + ui_h)

		# Reference points for alignment
		center_x = ui_left_x + (ui_w / 2)
		top_y = ui_bottom_y + ui_h

		# 2. SCORE Section
		score_label_y = top_y - 2.0
		stddraw.setPenColor(Color(170, 180, 190))  # Soft gray for labels
		stddraw.setFontFamily("Helvetica")
		stddraw.setFontSize(20)
		stddraw.boldText(center_x, score_label_y, "SCORE")

		stddraw.setPenColor(Color(255, 255, 255))  # Bright white for the number
		stddraw.setFontSize(28)
		stddraw.boldText(center_x, score_label_y - 1.5, str(self.score))

		# 3. HOLD Section
		hold_label_y = top_y - 7.0
		stddraw.setPenColor(Color(170, 180, 190))
		stddraw.setFontSize(20)
		stddraw.boldText(center_x, hold_label_y, "HOLD")

		if self.held_tetromino is not None:
			h_tiles, _ = self.held_tetromino.get_min_bounded_tile_matrix()
			h_rows, h_cols = h_tiles.shape
			h_off_x = center_x - (h_cols / 2.0)
			h_off_y = hold_label_y - h_rows - 1.0
			for r in range(h_rows):
				for c in range(h_cols):
					if h_tiles[r][c] is not None:
						h_tiles[r][c].draw(
							Point(
								h_off_x + c + 0.5,
								h_off_y
								+ (h_rows - 1 - r)
								+ 0.5,
							),
							length=1,
						)

		# 4. NEXT Section
		next_label_y = top_y - 13.0
		stddraw.setPenColor(Color(170, 180, 190))
		stddraw.setFontSize(20)
		stddraw.boldText(center_x, next_label_y, "NEXT")

		if self.next_tetromino is not None:
			n_tiles, _ = self.next_tetromino.get_min_bounded_tile_matrix()
			n_rows, n_cols = n_tiles.shape
			n_off_x = center_x - (n_cols / 2.0)
			n_off_y = next_label_y - n_rows - 1.0
			for r in range(n_rows):
				for c in range(n_cols):
					if n_tiles[r][c] is not None:
						n_tiles[r][c].draw(
							Point(
								n_off_x + c + 0.5,
								n_off_y
								+ (n_rows - 1 - r)
								+ 0.5,
							),
							length=1,
						)

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
		"""Merge vertically adjacent tiles and shift above tiles down.

		Returns:
			The total points gained by merges (sum of merged tile values).
		"""
		total_points = 0

		for column_index in range(self.grid_width):
			row_index = 0

			while row_index < self.grid_height - 1:
				lower_tile = self.tile_matrix[row_index][column_index]
				upper_tile = self.tile_matrix[row_index + 1][
					column_index
				]

				if (
					lower_tile is not None
					and upper_tile is not None
					and getattr(lower_tile, "number", None)
					== getattr(upper_tile, "number", None)
				):
					# Merge the tiles
					new_value = lower_tile.number * 2
					lower_tile.set_number(new_value)
					total_points += new_value

					# Check for win condition
					if (
						new_value >= WIN_CONDITION
						and not self.kept_playing
					):
						self.game_won = True

					# Shift all tiles above the merge down
					# by one cell to close the gap
					for shift_row in range(
						row_index + 1, self.grid_height - 1
					):
						self.tile_matrix[shift_row][
							column_index
						] = self.tile_matrix[shift_row + 1][
							column_index
						]

					# Clear the topmost cell in the column
					self.tile_matrix[self.grid_height - 1][
						column_index
					] = None

					# Do not advance row_index.
					# This allows the newly dropped tile
					# to chain merge with the current lower_tile
					# on the next loop iteration.
					continue

				# Move to the next pair
				row_index += 1

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
