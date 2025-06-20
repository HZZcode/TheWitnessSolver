from abc import ABC
from collections.abc import Callable
from copy import deepcopy
from enum import Enum, StrEnum, auto
from dataclasses import dataclass, field
from itertools import product
from random import randint, choice
from typing import Self, TypeGuard

from multipledispatch import dispatch

from GetId import id_getter
from NoRepr import no_repr


class Position(ABC):
    ...


def is_point(pos: Position) -> TypeGuard['Coordinate']:
    return isinstance(pos, Coordinate) and pos.type is not CoordinateType.Grid


def is_segment(pos: Position) -> TypeGuard['SegmentPos']:
    return isinstance(pos, SegmentPos)


def is_grid(pos: Position) -> TypeGuard['Coordinate']:
    return isinstance(pos, Coordinate) and pos.type is not CoordinateType.Point


@no_repr
class SegmentDirection(Enum):
    X = (1, 0)
    Y = (0, 1)

    def __init__(self, x: int, y: int):
        self._value_ = (x, y)
        self.x = x
        self.y = y

    def __str__(self) -> str:
        if self == SegmentDirection.X:
            return 'X'
        else:  # SegmentDirection.Y
            return 'Y'


@no_repr
class CoordinateType(StrEnum):
    Point = auto()
    Grid = auto()
    Unknown = auto()

    def __str__(self) -> str:
        match self:
            case CoordinateType.Point:
                return "[Point]"
            case CoordinateType.Grid:
                return "[Grid]"
            case _:
                return ""

    def __eq__(self, other: Self) -> bool:
        return self is other or self is CoordinateType.Unknown or other is CoordinateType.Unknown

    @staticmethod
    def unknown():
        return CoordinateType.Unknown


@dataclass(frozen=True)
class Coordinate(Position):
    x: int
    y: int
    type: CoordinateType = field(default_factory=CoordinateType.unknown, kw_only=True)  # Used only in generating

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self) -> str:
        return f"{self.type}({self.x}, {self.y})"

    def __add__(self, other: SegmentDirection | Self) -> Self:
        return Coordinate(self.x + other.x, self.y + other.y, type=self.type)

    def __sub__(self, other: SegmentDirection | Self) -> Self:
        return Coordinate(self.x - other.x, self.y - other.y, type=self.type)

    def __radd__(self, other: SegmentDirection | Self) -> Self:
        return Coordinate(self.x + other.x, self.y + other.y, type=self.type)

    def nears(self) -> list['SegmentPos']:
        return [SegmentPos(self, SegmentDirection.X), SegmentPos(self + SegmentDirection.Y, SegmentDirection.X),
                SegmentPos(self, SegmentDirection.Y), SegmentPos(self + SegmentDirection.X, SegmentDirection.Y)]

    def near(self, other: Self):
        return abs(self.x - other.x) + abs(self.y - other.y) == 1


@no_repr
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


@no_repr
@dataclass
class BoardPart:
    grids: set[Coordinate] = field(default_factory=set)
    rotate: bool = field(default=False, kw_only=True)
    negative: bool = field(default=False, kw_only=True)
    id: int = field(default_factory=id_getter(), kw_only=True)

    @dataclass
    class BoundBox:
        x_min: int
        y_min: int
        x_max: int
        y_max: int

    @property
    def points(self) -> set[Coordinate]:
        return {point for grid in self.grids
                for point in [grid, grid + SegmentDirection.X, grid + SegmentDirection.Y,
                              grid + SegmentDirection.X + SegmentDirection.Y]}

    @property
    def segments(self) -> set[SegmentPos]:
        return {segment for grid in self.grids for segment in grid.nears()}

    @property
    def bound_box(self) -> BoundBox:
        x_set = {grid.x for grid in self.grids}
        y_set = {grid.y for grid in self.grids}
        return self.BoundBox(min(x_set), min(y_set), max(x_set), max(y_set))

    def rotatable(self) -> Self:
        self.rotate = True
        return self

    def __str__(self):
        return ('{' + ','.join(map(str, self.grids)) + '}'
                + ('(fixed)' if not self.rotate else '')
                + ('(negative)' if self.negative else ''))

    def __eq__(self, other) -> bool:
        return isinstance(other, BoardPart) and self.id == other.id

    def __neg__(self) -> Self:
        """Invert the `negative` property."""
        copied = deepcopy(self)
        copied.negative = not self.negative
        return copied

    def __len__(self) -> int:
        """The count of grids; might be negative."""
        l = len(self.grids)
        return -l if self.negative else l

    def __sub__(self, other: Self) -> set[Coordinate]:
        """Returns the differences between two part."""
        return {grid1 - grid2 for grid1 in self.grids for grid2 in other.grids}

    def __add__(self, other: Coordinate) -> Self:
        """Translates a part with offset."""
        return BoardPart({grid + other for grid in self.grids})

    def union(self, other: Self) -> Self:
        return BoardPart(self.grids.union(other.grids))

    def __and__(self, other: Self) -> list[Self]:
        """Combines two positive parts."""
        assert not self.negative and not other.negative
        if self.rotate:
            return [part for rotated in self.rotations() for part in rotated & other]
        if other.rotate:
            return other & self
        x_diffs = range(self.bound_box.x_min - other.bound_box.x_max - 1,
                        self.bound_box.x_max - other.bound_box.x_min + 2)
        y_diffs = range(self.bound_box.y_min - other.bound_box.y_max - 1,
                        self.bound_box.y_max - other.bound_box.y_min + 2)
        return [self.union(moved) for dx in x_diffs for dy in y_diffs
                if self.near(moved := other + Coordinate(dx, dy))
                if len(self ^ moved) == 0]

    def __le__(self, other: Self) -> bool:
        """Whether a part is included in another."""
        return self.grids <= other.grids

    def __xor__(self, other: Self) -> Self:
        """Intersection of two parts."""
        return BoardPart(self.grids.intersection(other.grids))

    def near(self, other: Self) -> bool:
        return any(pos1.near(pos2) for pos1 in self.grids for pos2 in other.grids)

    def diff(self, other: Self) -> Self:
        return BoardPart({grid for grid in self.grids if grid not in other.grids})

    def translate(self, rotation: Rotation) -> Self:
        return BoardPart({rotation(grid) for grid in self.grids}, rotate=False)

    def rotations(self) -> list[Self]:
        return [self.translate(rotation) for rotation in Rotation.values()] if self.rotate else [self]

    def match(self, parts: list[Self]) -> bool:
        if self.negative:
            return (-self).match([-part for part in parts])
        negatives: list[BoardPart] = [part for part in parts if part.negative]
        if len(negatives) != 0:
            return any(added.match([part for part in parts if part != neg])
                       for neg in negatives for added in (-neg) & self)
        if self.rotate or any(part.rotate for part in parts):
            return any(rotated.match(list(rotated_parts)) for rotated in self.rotations()
                       for rotated_parts in product(*[part.rotations() for part in parts]))
        if len(self) == len(parts) == 0:
            return True
        if len(self) != sum(map(len, parts)):
            return False
        part = parts[0]
        return any(self.diff(part + diff).match(parts[1:]) for diff in self - part if part + diff <= self)

    def split(self) -> tuple[Self, Self]:
        if randint(0, 2) == 0:
            negative = choice(common_parts)
            return -negative, choice(self & negative)
        else:
            grid_sets = [set(), set()]
            for pos in self.grids:
                grid_sets[randint(0, 1)].add(pos)
            return tuple(BoardPart(grids, rotate=True, negative=self.negative) for grids in grid_sets)


common_parts: list[BoardPart] = [
    BoardPart({Coordinate(0, 0)}, rotate=True),  # ['#']
    BoardPart({Coordinate(0, 0), Coordinate(0, 1)}, rotate=True),  # ['##']
    BoardPart({Coordinate(0, 0), Coordinate(0, 1), Coordinate(0, 2)}, rotate=True),  # ['###']
    BoardPart({Coordinate(0, 0), Coordinate(0, 1), Coordinate(1, 0)}, rotate=True),  # ['#', '##']
    BoardPart({Coordinate(0, 0), Coordinate(0, 1), Coordinate(0, 2), Coordinate(0, 3)}, rotate=True),  # ['####']
    BoardPart({Coordinate(0, 0), Coordinate(0, 1), Coordinate(1, 0), Coordinate(1, 1)}, rotate=True),  # ['##', '##']
    BoardPart({Coordinate(0, 0), Coordinate(0, 1), Coordinate(0, 2), Coordinate(1, 0)}, rotate=True),  # ['#', '###']
    BoardPart({Coordinate(0, 0), Coordinate(0, 1), Coordinate(0, 2), Coordinate(1, 1)}, rotate=True),  # [' #', '###']
]
