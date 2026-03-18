"""Point class for representing 2D coordinates in the game grid.

A Point represents a location in 2D space with x and y coordinates,
used for tracking positions of game pieces and grid cells.
"""


class Point:
    """Represents a point as a location in 2D space.

    Attributes:
        x (int): The x-coordinate of the point.
        y (int): The y-coordinate of the point.
    """

    def __init__(self, x: int = 0, y: int = 0) -> None:
        """Initialize a point at the given location.

        Args:
            x: The x-coordinate. Defaults to 0.
            y: The y-coordinate. Defaults to 0.
        """
        self.x = x
        self.y = y

    def translate(self, dx: int, dy: int) -> None:
        """Move this point by the given deltas.

        Args:
            dx: The change in x-coordinate.
            dy: The change in y-coordinate.
        """
        self.x += dx
        self.y += dy

    def move(self, x: int, y: int) -> None:
        """Move this point to the given location.

        Args:
            x: The new x-coordinate.
            y: The new y-coordinate.
        """
        self.x = x
        self.y = y

    def __str__(self) -> str:
        """Return the string representation of this point.

        Returns:
            A string in the format '(x, y)'.
        """
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Return the representation of this point.

        Returns:
            A string representation suitable for debugging.
        """
        return f"Point(x={self.x}, y={self.y})"
