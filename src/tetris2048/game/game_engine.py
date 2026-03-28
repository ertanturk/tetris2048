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
	GRID_HEIGHT: int = 20
	GRID_WIDTH: int = 12
	CELL_SIZE: int = 40

	def __init__(self) -> None:
		"""Initialize the game engine with default settings."""
		self.grid_height: int = self.GRID_HEIGHT
		self.grid_width: int = self.GRID_WIDTH
		self.cell_size: int = self.CELL_SIZE

		# Calculate canvas dimensions
		self.canvas_height: int = self.cell_size * self.grid_height
		self.canvas_width: int = self.cell_size * self.grid_width

		# Initialize the game grid
		game_grid_cls = _lazy_import_game_grid()
		self.grid: GameGrid = game_grid_cls(self.grid_height, self.grid_width)
		self.current_tetromino: Tetromino | None = None

		# Bag for tetromino randomization
		self._bag: list[str] = []

		# Rotation track for tetromino rotation
		self._rotation_degree: int = 0

		# Logger for this module
		self._logger: logging.Logger = logging.getLogger(__name__)

	def setup_display(self) -> None:
		"""Set up the display canvas and coordinate system."""
		stddraw = _lazy_import_stddraw()
		tetromino_cls = _lazy_import_tetromino()
		stddraw.setCanvasSize(self.canvas_width, self.canvas_height)  # pyright: ignore[reportAny]
		stddraw.setXscale(-0.5, self.grid_width - 0.5)  # pyright: ignore[reportAny]
		stddraw.setYscale(-0.5, self.grid_height - 0.5)  # pyright: ignore[reportAny]

		# Set grid dimensions for Tetromino class
		tetromino_cls.grid_height = self.grid_height
		tetromino_cls.grid_width = self.grid_width

	def _refill_bag(self) -> None:
		"""Refill and shuffle the bag of tetromino types."""
		# Choose the set of shapes you support here. Make sure Tetromino.SHAPES
		# contains entries for every name in this list.
		bag = ["I", "O", "Z", "L", "T", "S", "J"]
		# Fisher-Yates shuffle using secrets for cryptographically-strong
		# randomness.
		for i in range(len(bag) - 1, 0, -1):
			j = secrets.randbelow(i + 1)
			bag[i], bag[j] = bag[j], bag[i]
		self._bag = bag

	def create_tetromino(self) -> "Tetromino":
		"""Create a new random tetromino.

		Returns:
			A new Tetromino with a random shape.
		"""
		tetromino_cls = _lazy_import_tetromino()
		# Refill bag if empty
		if not self._bag:
			self._refill_bag()

		shape = self._bag.pop()
		# Log spawn for verification
		self._logger.debug("Spawning tetromino: %s", shape)
		return tetromino_cls(shape)

	def spawn_tetromino(self) -> None:
		"""Create and spawn a new tetromino into the game grid."""
		self.current_tetromino = self.create_tetromino()
		self._rotation_degree = 0
		self.grid.current_tetromino = self.current_tetromino

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
		stddraw.clear(background_color)  # pyright: ignore[reportAny]

		# Get the directory of this file and build path to menu image
		current_dir = Path(__file__).resolve().parent
		img_file = current_dir / ".." / ".." / "images" / "menu_image.png"

		# Display image if it exists
		img_center_x = (self.grid_width - 1) / 2
		img_center_y = self.grid_height - 7

		if img_file.exists():
			image_to_display = picture_cls(str(img_file))
			stddraw.picture(image_to_display, img_center_x, img_center_y)  # pyright: ignore[reportAny]

		# Draw start button
		button_w, button_h = self.grid_width - 1.5, 2
		button_blc_x = img_center_x - button_w / 2
		button_blc_y = 4

		stddraw.setPenColor(button_color)  # pyright: ignore[reportAny]
		stddraw.filledRectangle(button_blc_x, button_blc_y, button_w, button_h)  # pyright: ignore[reportAny]

		# Draw button text
		stddraw.setFontFamily("Arial")  # pyright: ignore[reportAny]
		stddraw.setFontSize(25)  # pyright: ignore[reportAny]
		stddraw.setPenColor(text_color)  # pyright: ignore[reportAny]
		stddraw.text(img_center_x, 5, "Click Here to Start the Game")  # pyright: ignore[reportAny]

		# Wait for user click
		while True:
			stddraw.show(50)  # pyright: ignore[reportAny]
			if stddraw.mousePressed():  # pyright: ignore[reportAny]
				mouse_x, mouse_y = (  # pyright: ignore[reportAny]
					stddraw.mouseX(),  # pyright: ignore[reportAny]
					stddraw.mouseY(),  # pyright: ignore[reportAny]
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

	def rotation_track(self: "GameEngine", key_typed: str) -> None:
		"""Track rotation requests and attempt rotation.

		When the user presses the rotation key (here we treat 'up'
		as rotate +90 degrees clockwise), we call the tetromino's rotate
		method with a 90-degree increment and update the tracked
		rotation degrees when the rotation is successfully applied.

		Args:
			key_typed: the typed key (from stddraw.nextKeyTyped()).
		"""
		# Only respond to rotation key
		if key_typed != "up":
			return

		# No current tetromino -> nothing to rotate
		if self.current_tetromino is None:
			return

		rotation_step = 90
		rotated = self.current_tetromino.rotate(rotation_step, self.grid)

		if rotated:
			if self._rotation_degree is None:
				self._rotation_degree = 0
			self._rotation_degree = (
				self._rotation_degree + rotation_step
			) % 360

	def handle_input(self) -> None:
		"""Handle keyboard input for tetromino movement."""
		stddraw = _lazy_import_stddraw()
		if not stddraw.hasNextKeyTyped():  # pyright: ignore[reportAny]
			return

		key_typed = stddraw.nextKeyTyped()  # pyright: ignore[reportAny]

		if self.current_tetromino is None:
			stddraw.clearKeysTyped()  # pyright: ignore[reportAny]
			return

		if key_typed == "left":
			_ = self.current_tetromino.move("left", self.grid)
		elif key_typed == "right":
			_ = self.current_tetromino.move("right", self.grid)
		elif key_typed == "down":
			_ = self.current_tetromino.move("down", self.grid)

		self.rotation_track(key_typed)
		stddraw.clearKeysTyped()  # pyright: ignore[reportAny]

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
			success = self.current_tetromino.move("down", self.grid)

			# If tetromino can't move down, lock it on the grid
			if not success:
				tiles, pos = (
					self.current_tetromino.get_min_bounded_tile_matrix(
						return_position=True
					)
				)
				if pos is None:
					msg = "Position not returned by tetromino"
					raise RuntimeError(msg)
				self.grid.update_grid(tiles, pos)  # pyright: ignore[reportUnusedCallResult]

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
