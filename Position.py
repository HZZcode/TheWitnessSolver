from abc import ABC
from collections.abc import Callable
from enum import Enum
from dataclasses import dataclass, field
from itertools import product
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

    def __repr__(self):
        return str(self)

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


class Rotation(Enum):
    Rotate0 = lambda coordinate: Coordinate(coordinate.x, coordinate.y)
    Rotate90 = lambda coordinate: Coordinate(coordinate.y, -coordinate.x)
    Rotate180 = lambda coordinate: Coordinate(-coordinate.x, -coordinate.y)
    Rotate270 = lambda coordinate: Coordinate(-coordinate.y, coordinate.x)

    @staticmethod
    def values():
        return [Rotation.Rotate0, Rotation.Rotate90, Rotation.Rotate180, Rotation.Rotate270]

    def __init__(self, translation: Callable[[Coordinate], Coordinate]):
        self.translation = translation

    def __call__(self, coordinate: Coordinate) -> Coordinate:
        return self.translation(coordinate)


@dataclass
class BoardPart:
    grids: set[Coordinate] = field(default_factory=set)
    rotate: bool = field(default=False, kw_only=True)

    @property
    def points(self) -> set[Coordinate]:
        return {point for grid in self.grids
                for point in [grid, grid + SegmentDirection.X, grid + SegmentDirection.Y,
                              grid + SegmentDirection.X + SegmentDirection.Y]}

    @property
    def segments(self) -> set[SegmentPos]:
        return {segment for grid in self.grids for segment in grid.nears()}

    def __str__(self):
        return '{' + ','.join(map(str, self.grids)) + '}'

    @staticmethod
    def from_str(rows: list[str], *, rotate: bool = False) -> 'BoardPart':
        """e.g. from_str(['#', '# ', '##']) -> {(0, 0), (0, 1), (0, 2), (1, 0)}"""
        return BoardPart({Coordinate(-row, column) for row, s in enumerate(rows)
                          for column, c in enumerate(s) if c != ' '}, rotate=rotate)

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

    def translate(self, rotation: Rotation) -> Self:
        return BoardPart({rotation(grid) for grid in self.grids}, rotate=False)

    def rotations(self) -> list[Self]:
        return [self.translate(rotation) for rotation in Rotation.values()] if self.rotate else [self]

    def match(self, parts: list[Self]) -> bool:
        if self.rotate or any(part.rotate for part in parts):
            return any(rotated.match(list(rotated_parts)) for rotated in self.rotations()
                       for rotated_parts in product(*[part.rotations() for part in parts]))
        else:
            if len(self) == len(parts) == 0:
                return True
            if len(self) != sum(map(len, parts)):
                return False
            part = parts[0]
            return any(self.diff(part + diff).match(parts[1:]) for diff in self - part if part + diff <= self)
