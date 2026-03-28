"""Tetromino class for representing Tetris pieces.

A Tetromino is a game piece composed of four tiles arranged in various shapes
(I, O, T, S, Z, L, J). This implementation currently supports I, O, and Z shapes.
"""

import copy as cp
import secrets
from typing import TYPE_CHECKING, ClassVar, override

import numpy as np

from tetris2048.core.point import Point
from tetris2048.core.tile import Tile

if TYPE_CHECKING:
	from tetris2048.game.game_grid import GameGrid


class Tetromino:
	"""Represents a Tetris piece (tetromino).

	A Tetromino is composed of four tiles arranged in one of seven standard shapes.
	This class handles the piece's position, rotation, and movement on the grid.

	Attributes:
		type (str): The shape type ('I', 'O', 'Z', etc.)
		tile_matrix (np.ndarray): 2D matrix of tiles in this tetromino.
		bottom_left_cell (Point): The position of the bottom-left corner.
		grid_height (int): The height of the game grid (class variable).
		grid_width (int): The width of the game grid (class variable).
	"""

	# Standard Tetromino shapes column and row values
	SHAPES: ClassVar[dict[str, list[tuple[int, int]]]] = {
		"I": [(1, 0), (1, 1), (1, 2), (1, 3)],
		"O": [(0, 0), (0, 1), (1, 0), (1, 1)],
		"Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
		"S": [(1, 0), (2, 0), (0, 1), (1, 1)],
		"T": [(1, 0), (0, 1), (1, 1), (2, 1)],
		"L": [(0, 0), (0, 1), (0, 2), (1, 2)],
		"J": [(1, 0), (1, 1), (1, 2), (0, 2)],
	}

	def _spawn_tile_number(self) -> int:
		"""Return initial tile number: 90% chance 2, 10% chance 4.

		Matches common 2048 spawn behavior where most new tiles are 2 and 4.
		"""
		# 1 out of 10 chance to be a 4
		return 4 if secrets.randbelow(10) == 0 else 2

	grid_height: int = 20
	grid_width: int = 12

	def __init__(self, shape_type: str) -> None:
		"""Initialize a tetromino with the given shape type.

		Args:
			shape_type: The shape type ('I', 'O', 'Z', etc.)
		"""
		self.type: str = shape_type

		# Determine the size of the tile matrix
		if self.type == "I":
			n = 4
		elif self.type == "O":
			n = 2
		else:  # Z and others
			n = 3

		# Create tile matrix
		self.tile_matrix: np.ndarray = np.full((n, n), None)

		# Place tiles according to the shape
		for i in range(4):
			col_index, row_index = self.SHAPES[self.type][i]
			self.tile_matrix[row_index][col_index] = Tile(
				self._spawn_tile_number()
			)

		self.bottom_left_cell: Point = Point()
		self.bottom_left_cell.y = self.grid_height - 1
		self.bottom_left_cell.x = secrets.randbelow(self.grid_width - n + 1)

	def get_cell_position(self, row: int, col: int) -> Point:
		"""Get the position of a cell in the tetromino.

		Args:
			row: The row index in the tile matrix.
			col: The column index in the tile matrix.

		Returns:
			The position of the cell on the game grid.
		"""
		n = len(self.tile_matrix)
		position = Point()
		position.x = self.bottom_left_cell.x + col
		position.y = self.bottom_left_cell.y + (n - 1) - row
		return position

	def get_min_bounded_tile_matrix(
		self, *, return_position: bool = False
	) -> tuple[np.ndarray, Point | None]:
		"""Get the minimal bounding tile matrix without empty rows/columns.

		`return_position` is a keyword-only boolean. If True, the function
		also returns the bottom-left corner position of the bounded matrix.

		Returns:
			If `return_position` is False: tuple(tile_matrix, None).
			If `return_position` is True: tuple(tile_matrix, position).
		"""
		n = len(self.tile_matrix)
		min_row, max_row = n - 1, 0
		min_col, max_col = n - 1, 0

		# Find the bounding box of non-empty cells
		for row in range(n):
			for col in range(n):
				if self.tile_matrix[row][col] is not None:
					min_row = min(min_row, row)
					max_row = max(max_row, row)
					min_col = min(min_col, col)
					max_col = max(max_col, col)

		# Copy the bounded tiles
		bounded_copy = np.full(
			(max_row - min_row + 1, max_col - min_col + 1), None
		)
		for row in range(min_row, max_row + 1):
			for col in range(min_col, max_col + 1):
				if self.tile_matrix[row][col] is not None:
					row_ind = row - min_row
					col_ind = col - min_col
					bounded_copy[row_ind][col_ind] = cp.deepcopy(
						self.tile_matrix[row][col]
					)

		if not return_position:
			return bounded_copy, None

		# Compute the new bottom-left corner position
		blc_position = cp.copy(self.bottom_left_cell)
		blc_position.translate(min_col, (n - 1) - max_row)
		return bounded_copy, blc_position

	def draw(self) -> None:
		"""Draw this tetromino on the game grid."""
		n = len(self.tile_matrix)
		for row in range(n):
			for col in range(n):
				tile = self.tile_matrix[row][col]
				if isinstance(tile, Tile):
					position = self.get_cell_position(row, col)
					# Only draw tiles inside the grid
					if position.y < self.grid_height:
						tile.draw(position)

	def move(self, direction: str, game_grid: "GameGrid") -> bool:
		"""Move this tetromino in the given direction.

		Args:
			direction: The direction to move ('left', 'right', or 'down').
			game_grid: The game grid to check for collisions.

		Returns:
			True if the move was successful, False otherwise.
		"""
		if not self.can_be_moved(direction, game_grid):
			return False

		if direction == "left":
			self.bottom_left_cell.x -= 1
		elif direction == "right":
			self.bottom_left_cell.x += 1
		elif direction == "down":
			self.bottom_left_cell.y -= 1

		return True

	def rotate(self, angle: int, game_grid: "GameGrid") -> bool:
		"""Rotate this tetromino by the given angle.

		Args:
			angle: The angle to rotate (in degrees, clockwise).
			game_grid: The game grid to check for collisions.

		Returns:
			True if the rotation was successful, False otherwise.
		"""
		# O piece is invariant under rotation
		if self.type == "O":
			return True

		# numpy.rot90 rotates counter-clockwise by default, k is number of
		# 90-degree turns to rotate clockwise.
		rotated_matrix = np.rot90(self.tile_matrix, k=-angle // 90)
		n = len(rotated_matrix)

		# For each occupied cell in the rotated matrix compute
		# its global position using the same bottom_left_cell anchor and check
		# the candidate location.
		for row in range(n):
			for col in range(n):
				if rotated_matrix[row][col] is None:
					continue

				# Compute the global position for this rotated
				# local cell.
				new_pos = Point()
				new_pos.x = self.bottom_left_cell.x + col
				new_pos.y = self.bottom_left_cell.y + (n - 1) - row

				if not self.can_be_rotated(new_pos, game_grid):
					return False
		self.tile_matrix = rotated_matrix
		return True

	def can_be_rotated(self, position: Point, game_grid: "GameGrid") -> bool:
		"""Check if it is valid to rotate a tetromino."""
		# Horizontal bounds check
		if position.x < 0 or position.x >= game_grid.grid_width:
			return False

		# Below bottom is invalid
		if position.y < 0:
			return False

		if position.y >= game_grid.grid_height:
			return True

		return not game_grid.is_occupied(position.y, position.x)

	def can_be_moved(self, direction: str, game_grid: "GameGrid") -> bool:
		"""Check if this tetromino can be moved in the given direction.

		Args:
			direction: The direction to check ('left', 'right', or 'down').
			game_grid: The game grid to check for collisions.

		Returns:
			True if the move is valid, False otherwise.
		"""
		if direction == "left":
			return self._can_move_left(game_grid)
		if direction == "right":
			return self._can_move_right(game_grid)
		if direction == "down":
			return self._can_move_down(game_grid)
		return False

	def _can_move_left(self, game_grid: "GameGrid") -> bool:
		"""Check whether this tetromino can move left."""
		n = len(self.tile_matrix)
		for row in range(n):
			for col in range(n):
				if self.tile_matrix[row][col] is None:
					continue
				leftmost = self.get_cell_position(row, col)
				if leftmost.x == 0:
					return False
				if game_grid.is_occupied(leftmost.y, leftmost.x - 1):
					return False
				break
		return True

	def _can_move_right(self, game_grid: "GameGrid") -> bool:
		"""Check whether this tetromino can move right."""
		n = len(self.tile_matrix)
		for row in range(n):
			for col_offset in range(n):
				col = n - 1 - col_offset
				if self.tile_matrix[row][col] is None:
					continue
				rightmost = self.get_cell_position(row, col)
				if rightmost.x == self.grid_width - 1:
					return False
				if game_grid.is_occupied(rightmost.y, rightmost.x + 1):
					return False
				break
		return True

	def _can_move_down(self, game_grid: "GameGrid") -> bool:
		"""Check whether this tetromino can move down."""
		n = len(self.tile_matrix)
		for col in range(n):
			for row in range(n - 1, -1, -1):
				if self.tile_matrix[row][col] is None:
					continue
				bottommost = self.get_cell_position(row, col)
				if bottommost.y == 0:
					return False
				if game_grid.is_occupied(
					bottommost.y - 1, bottommost.x
				):
					return False
				break
		return True

	@override
	def __str__(self) -> str:
		"""Return the string representation of this tetromino.

		Returns:
			A string showing the tetromino type.
		"""
		return f"Tetromino({self.type})"

	@override
	def __repr__(self) -> str:
		"""Return the representation of this tetromino.

		Returns:
			A string representation suitable for debugging.
		"""
		return (
			f"Tetromino(type='{self.type}', "
			f"position={self.bottom_left_cell})"
		)
