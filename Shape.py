from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from Position import Position, Coordinate, SegmentPos
from Path import Path

if TYPE_CHECKING:
    from Board import Board, BoardPart


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


@dataclass
class Square(Shape):
    color: str

    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        if isinstance(pos, Coordinate):
            part: 'BoardPart' = board.find_including_part(pos, path)
            return all(square.color == self.color for grid in part.grids
                       for square in board.grids[grid].shapes if isinstance(square, Square))
        else:
            return False
