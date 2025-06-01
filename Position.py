from abc import ABC
from enum import Enum
from dataclasses import dataclass
from typing import Self


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

    def __add__(self, other: SegmentDirection) -> Self:
        return Coordinate(self.x + other.x, self.y + other.y)

    def __sub__(self, other: SegmentDirection) -> Self:
        return Coordinate(self.x - other.x, self.y - other.y)

    def __radd__(self, other: SegmentDirection) -> Self:
        return Coordinate(self.x + other.x, self.y + other.y)


@dataclass(frozen=True, unsafe_hash=True)
class SegmentPos(Position):
    coordinate: Coordinate
    direction: SegmentDirection

    @staticmethod
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
