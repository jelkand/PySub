"""This module contains enums and utility classes for PySub"""

from collections import namedtuple
from enum import Enum

class Direction(Enum):
    """Simple enum for directions"""
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'

class Equipment(Enum):
    """Enumeration of Equipment.
    Only equipment to move, ping, and fire is available."""
    NONE = "None"
    SONAR = "Sonar"
    TORPEDO = "Torpedo"

class Coordinate(namedtuple('Coordinate', ['x', 'y'])):
    """Represents a map coordinate"""
    __slots__ = ()
    def __str__(self):
        return "{0}|{1}".format(self.x, self.y)
    def shifted(self, direction):
        """Returns a new coordinate shifted in the given direction"""
        if direction == Direction.NORTH:
            return Coordinate(self.x, (self.y-1))
        elif direction == Direction.EAST:
            return Coordinate((self.x+1), self.y)
        elif direction == Direction.SOUTH:
            return Coordinate(self.x, (self.y + 1))
        elif direction == Direction.WEST:
            return Coordinate((self.x-1), self.y)

class MapSquare(Coordinate):
    """Represents a square on the map"""
    blocked = False
    object_size = 0
    foreign_object_size = 0

    def __init__(self, x, y):
        super().__init__(self, x, y)

    def is_empty(self):
        """Returns true if the map square has no obstacle and is not occupied"""
        return not self.blocked and self.object_size == 0

    def reset(self):
        """Resets the map square so it can be updated later"""
        self.object_size = 0
        self.foreign_object_size = 0
