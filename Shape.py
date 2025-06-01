from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from Position import Position, Coordinate
from Path import Path

if TYPE_CHECKING:
    from Board import Board


class Shape(ABC):
    @abstractmethod
    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        ...

class Hexagon(Shape):
    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        if isinstance(pos, Coordinate):
            return pos in path.points
        else:
            return pos in path.segments
