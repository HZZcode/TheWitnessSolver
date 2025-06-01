from abc import ABC
from enum import Enum
from dataclasses import dataclass, field
from typing import Self

from multipledispatch import dispatch


class Position(ABC):
    ...


class SegmentDirection(Enum):
    X = (1, 0)
    Y = (0, 1)

    def __init__(self, x: int, y: int):
        self._value_ = (x, y)
        self.x = x
        self.y = y


@dataclass(frozen=True, unsafe_hash=True)
class Coordinate(Position):
    x: int
    y: int

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __add__(self, other: SegmentDirection | Self) -> Self:
        return Coordinate(self.x + other.x, self.y + other.y)

    def __sub__(self, other: SegmentDirection | Self) -> Self:
        return Coordinate(self.x - other.x, self.y - other.y)

    def __radd__(self, other: SegmentDirection | Self) -> Self:
        return Coordinate(self.x + other.x, self.y + other.y)

    def nears(self) -> list['SegmentPos']:
        return [SegmentPos(self, SegmentDirection.X), SegmentPos(self + SegmentDirection.Y, SegmentDirection.X),
                SegmentPos(self, SegmentDirection.Y), SegmentPos(self + SegmentDirection.X, SegmentDirection.Y)]


@dataclass(frozen=True, unsafe_hash=True)
class SegmentPos(Position):
    coordinate: Coordinate
    direction: SegmentDirection

    def __str__(self) -> str:
        return f'{self.coordinate} ~ {self.coordinate + self.direction}'

    @staticmethod
    @dispatch(int, int, int, int)
    def between(x1: int, y1: int, x2: int, y2: int) -> 'SegmentPos':
        return SegmentPos.between(Coordinate(x1, y1), Coordinate(x2, y2))

    @staticmethod
    @dispatch(Coordinate, Coordinate)
    def between(p: Coordinate, q: Coordinate) -> 'SegmentPos':
        if p.x + 1 == q.x and p.y == q.y:
            return SegmentPos(p, SegmentDirection.X)
        if p.x == q.x + 1 and p.y == q.y:
            return SegmentPos(q, SegmentDirection.X)
        if p.x == q.x and p.y + 1 == q.y:
            return SegmentPos(p, SegmentDirection.Y)
        if p.x == q.x and p.y == q.y + 1:
            return SegmentPos(q, SegmentDirection.Y)
        raise ValueError(f'{p} and {q} are not in a segment')


@dataclass
class BoardPart:
    grids: set[Coordinate] = field(default_factory=set)
    rotate: bool = field(default=False)

    def __str__(self):
        return '{' + ','.join(map(str, self.grids)) + '}'

    def __len__(self) -> int:
        return len(self.grids)

    def __sub__(self, other: Self) -> set[Coordinate]:
        return {grid1 - grid2 for grid1 in self.grids for grid2 in other.grids}

    def __add__(self, other: Coordinate) -> Self:
        return BoardPart({grid + other for grid in self.grids})

    def __le__(self, other: Self) -> bool:
        return self.grids <= other.grids

    def diff(self, other: Self) -> Self:
        return BoardPart({grid for grid in self.grids if grid not in other.grids})

    def match(self, parts: list[Self]) -> bool:
        if not self.rotate:
            if len(self) == len(parts) == 0:
                return True
            if len(self) != sum(map(len, parts)):
                return False
            part = parts[0]
            return any(self.diff(part + diff).match(parts[1:]) for diff in self - part if part + diff <= self)
        else:
            return True # TODO
