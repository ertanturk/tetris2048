"""Main game engine for Tetris 2048.

This module contains the GameEngine class which orchestrates the game loop,
handles user input, and manages the overall game state.
"""

import logging
import secrets
import types
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from tetris2048.game.game_grid import GameGrid
	from tetris2048.game.tetromino import Tetromino
	from tetris2048.rendering.color import Color
	from tetris2048.rendering.picture import Picture


def _lazy_import_game_grid() -> type["GameGrid"]:
	"""Lazily import GameGrid to avoid circular imports."""
	from tetris2048.game.game_grid import GameGrid  # noqa: PLC0415

	return GameGrid


def _lazy_import_tetromino() -> type["Tetromino"]:
	"""Lazily import Tetromino to avoid circular imports."""
	from tetris2048.game.tetromino import Tetromino  # noqa: PLC0415

	return Tetromino


def _lazy_import_color() -> type["Color"]:
	"""Lazily import Color to avoid circular imports."""
	from tetris2048.rendering.color import Color  # noqa: PLC0415

	return Color


def _lazy_import_picture() -> type["Picture"]:
	"""Lazily import Picture to avoid circular imports."""
	from tetris2048.rendering.picture import Picture  # noqa: PLC0415

	return Picture


def _lazy_import_stddraw() -> types.ModuleType:
	"""Lazily import stddraw to avoid circular imports."""
	from tetris2048.rendering import stddraw  # noqa: PLC0415

	return stddraw


class GameEngine:
	"""The main game engine for Tetris 2048.

	Orchestrates the game loop, handles user input, manages tetrominoes,
	and controls game state transitions.
	"""

	# Game grid dimensions
	GRID_HEIGHT = 20
	GRID_WIDTH = 12
	CELL_SIZE = 40

	def __init__(self) -> None:
		"""Initialize the game engine with default settings."""
		self.grid_height = self.GRID_HEIGHT
		self.grid_width = self.GRID_WIDTH
		self.cell_size = self.CELL_SIZE

		# Calculate canvas dimensions
		self.canvas_height = self.cell_size * self.grid_height
		self.canvas_width = self.cell_size * self.grid_width

		# Initialize the game grid
		game_grid_cls = _lazy_import_game_grid()
		self.grid = game_grid_cls(self.grid_height, self.grid_width)
		self.current_tetromino: Tetromino | None = None

		# Logger for this module
		self._logger = logging.getLogger(__name__)

	def setup_display(self) -> None:
		"""Set up the display canvas and coordinate system."""
		stddraw = _lazy_import_stddraw()
		tetromino_cls = _lazy_import_tetromino()
		stddraw.setCanvasSize(self.canvas_width, self.canvas_height)
		stddraw.setXscale(-0.5, self.grid_width - 0.5)
		stddraw.setYscale(-0.5, self.grid_height - 0.5)

		# Set grid dimensions for Tetromino class
		tetromino_cls.grid_height = self.grid_height
		tetromino_cls.grid_width = self.grid_width

	def create_tetromino(self) -> "Tetromino":
		"""Create a new random tetromino.

		Returns:
			A new Tetromino with a random shape.
		"""
		tetromino_cls = _lazy_import_tetromino()
		tetromino_types = ["I", "O", "Z"]
		# Use secrets to avoid security lint about pseudo-random for crypto
		return tetromino_cls(secrets.choice(tetromino_types))

	def display_game_menu(self) -> None:
		"""Display the main game menu and wait for user to start.

		Shows an image, information text, and a clickable start button.
		Blocks until the user clicks the start button.
		"""
		color_cls = _lazy_import_color()
		picture_cls = _lazy_import_picture()
		stddraw = _lazy_import_stddraw()
		# Menu colors
		background_color = color_cls(42, 69, 99)
		button_color = color_cls(25, 255, 228)
		text_color = color_cls(31, 160, 239)

		# Clear background
		stddraw.clear(background_color)

		# Get the directory of this file and build path to menu image
		current_dir = Path(__file__).resolve().parent
		img_file = current_dir / ".." / ".." / "images" / "menu_image.png"

		# Display image if it exists
		img_center_x = (self.grid_width - 1) / 2
		img_center_y = self.grid_height - 7

		if img_file.exists():
			image_to_display = picture_cls(str(img_file))
			stddraw.picture(image_to_display, img_center_x, img_center_y)

		# Draw start button
		button_w, button_h = self.grid_width - 1.5, 2
		button_blc_x = img_center_x - button_w / 2
		button_blc_y = 4

		stddraw.setPenColor(button_color)
		stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)

		# Draw button text
		stddraw.setFontFamily("Arial")
		stddraw.setFontSize(25)
		stddraw.setPenColor(text_color)
		stddraw.text(img_center_x, 5, "Click Here to Start the Game")

		# Wait for user click
		while True:
			stddraw.show(50)
			if stddraw.mousePressed():
				mouse_x, mouse_y = (
					stddraw.mouseX(),
					stddraw.mouseY(),
				)
				# Check if click is inside button
				if (
					button_blc_x
					<= mouse_x
					<= button_blc_x + button_w
					and button_blc_y
					<= mouse_y
					<= button_blc_y + button_h
				):
					break

	def handle_input(self) -> None:
		"""Handle keyboard input for tetromino movement."""
		stddraw = _lazy_import_stddraw()
		if not stddraw.hasNextKeyTyped():
			return

		key_typed = stddraw.nextKeyTyped()

		if self.current_tetromino is None:
			return

		if key_typed == "left":
			self.current_tetromino.move("left", self.grid)
		elif key_typed == "right":
			self.current_tetromino.move("right", self.grid)
		elif key_typed == "down":
			self.current_tetromino.move("down", self.grid)

		stddraw.clearKeysTyped()

	def spawn_tetromino(self) -> None:
		"""Create and spawn a new tetromino into the game grid."""
		self.current_tetromino = self.create_tetromino()
		self.grid.current_tetromino = self.current_tetromino

	def run(self) -> None:
		"""Run the main game loop.

		Handles display setup, menu, and continuous game updates
		until the game ends.
		"""
		# Setup
		self.setup_display()
		self.display_game_menu()

		# Spawn first tetromino
		self.spawn_tetromino()
		if self.current_tetromino is None:
			msg = "Tetromino must be spawned"
			raise RuntimeError(msg)

		# Main game loop
		while not self.grid.game_over:
			# Handle user input
			self.handle_input()

			# Move tetromino down
			if self.current_tetromino is None:
				break
			success = self.current_tetromino.move("down", self.grid)

			# If tetromino can't move down, lock it on the grid
			if not success:
				if self.current_tetromino is None:
					msg = "Current tetromino missing"
					raise RuntimeError(msg)
				tiles, pos = (
					self.current_tetromino.get_min_bounded_tile_matrix(
						return_position=True
					)
				)
				if pos is None:
					msg = "Position not returned by tetromino"
					raise RuntimeError(msg)
				self.grid.update_grid(tiles, pos)

				# Spawn next tetromino
				self.spawn_tetromino()

			# Display the current state
			self.grid.display()

		# Game over
		self._logger.info("Game over")


def main() -> None:
	"""Main entry point for the game."""
	engine = GameEngine()
	engine.run()


if __name__ == "__main__":
	main()
