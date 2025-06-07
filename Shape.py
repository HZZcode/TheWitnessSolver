from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TYPE_CHECKING

from Position import Position, Coordinate
from Path import Path

if TYPE_CHECKING:
    from Board import Board, BoardPart


class Shape(ABC):
    @abstractmethod
    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        ...


class Colors(StrEnum):
    Red = auto()
    Orange = auto()
    Yellow = auto()
    Green = auto()
    Blue = auto()
    Purple = auto()
    White = auto()
    Black = auto()

    def __repr__(self) -> str:
        return str(self)


type ColorType = Colors | str


@dataclass
class Colored:
    color: ColorType


class Hexagon(Shape):
    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        if isinstance(pos, Coordinate):
            return pos in path.points
        else:
            return pos in path.segments


@dataclass
class Square(Shape, Colored):
    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        if isinstance(pos, Coordinate):
            part: 'BoardPart' = board.find_including_part(pos, path)
            return all(square.color == self.color for grid in part.grids
                       for square in board.grids[grid].shapes if isinstance(square, Square))
        else:
            return False


@dataclass
class Block(Shape):
    shape: 'BoardPart'

    @staticmethod
    def from_str(rows: list[str], *, rotate: bool = False, negative: bool = False) -> 'Block':
        """e.g. from_str(['#', '# ', '##']) -> {(0, 0), (0, 1), (0, 2), (1, 0)}"""
        from Position import BoardPart
        return Block(BoardPart({Coordinate(-row, column) for row, s in enumerate(rows)
                                for column, c in enumerate(s) if c != ' '}, rotate=rotate, negative=negative))

    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        if isinstance(pos, Coordinate):
            part: 'BoardPart' = board.find_including_part(pos, path)
            parts: list['BoardPart'] = [block.shape for grid in part.grids
                                        for block in board.grids[grid].shapes if isinstance(block, Block)]
            return part.match(parts)
        else:
            return False


@dataclass
class Star(Shape, Colored):
    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        if isinstance(pos, Coordinate):
            part: 'BoardPart' = board.find_including_part(pos, path)
            return sum(colored.color == self.color for grid in part.grids
                       for colored in board.grids[grid].shapes if isinstance(colored, Colored)) == 2
        else:
            return False


@dataclass
class Triangle(Shape):
    count: int

    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        if isinstance(pos, Coordinate):
            return sum(near in path.segments for near in pos.nears()) == self.count
        else:
            return False


class Jack(Shape):
    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        return True  # Its checking is implement in Board
