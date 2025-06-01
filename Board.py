from dataclasses import dataclass, field
from typing import Self

from Position import Coordinate, SegmentPos, Position, SegmentDirection
from Shape import Shape
from Path import Path


@dataclass
class BoardObject:
    shapes: list[Shape] = field(default_factory=list)

    def __post_init__(self):
        if self.shapes is None:
            self.shapes = []

    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        return all(shape.check(board, pos, path) for shape in self.shapes)


class Point(BoardObject):
    """Its x ranges in [0, width], y ranges in [0, height], and the left-down grid is (0,0)."""


class Segment(BoardObject):
    """Represents a segment from `coordinate` to `coordinate` + `direction`."""
    connected: bool

    def with_connected(self, connected: bool) -> Self:
        self.connected = connected
        return self


class Grid(BoardObject):
    """Its x ranges in [0, width), y ranges in [0, height), and the left-down grid is (0,0)."""


@dataclass
class Board:
    width: int
    height: int
    start_point: Coordinate
    end_point: Coordinate
    points: dict[Coordinate, Point] = field(default_factory=dict)
    segments: dict[SegmentPos, Segment] = field(default_factory=dict)
    grids: dict[Coordinate, Grid] = field(default_factory=dict)

    def in_board(self, point: Coordinate) -> bool:
        return 0 <= point.x <= self.width and 0 <= point.y <= self.height

    def nears(self, point: Coordinate) -> list[Coordinate]:
        return list(filter(self.in_board, [
            point + SegmentDirection.X, point - SegmentDirection.X,
            point + SegmentDirection.Y, point - SegmentDirection.Y
        ]))

    def is_connected(self, pos: SegmentPos) -> bool:
        return pos not in self.segments or self.segments[pos].connected

    def check(self, path: Path) -> bool:
        return (all(point.check(self, pos, path) for pos, point in self.points.items())
                and all(segment.check(self, pos, path) for pos, segment in self.segments.items())
                and all(grid.check(self, pos, path) for pos, grid in self.grids.items()))
