from dataclasses import dataclass, field
from typing import Self

from DefaultedDict import DefaultedDict
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


@dataclass
class Segment(BoardObject):
    """Represents a segment from `coordinate` to `coordinate` + `direction`."""
    connected: bool = field(default=True)

    def with_connected(self, connected: bool) -> Self:
        self.connected = connected
        return self


class Grid(BoardObject):
    """Its x ranges in [0, width), y ranges in [0, height), and the left-down grid is (0,0)."""


@dataclass
class BoardPart:
    grids: set[Coordinate] = field(default_factory=set)


@dataclass
class Board:
    width: int
    height: int
    start_point: Coordinate
    end_point: Coordinate
    points: dict[Coordinate, Point] = field(default_factory=DefaultedDict(Coordinate, Point))
    segments: dict[SegmentPos, Segment] = field(default_factory=DefaultedDict(SegmentPos, Segment))
    grids: dict[Coordinate, Grid] = field(default_factory=DefaultedDict(Coordinate, Grid))

    def in_board(self, point: Coordinate) -> bool:
        return 0 <= point.x <= self.width and 0 <= point.y <= self.height

    def nears(self, point: Coordinate) -> list[Coordinate]:
        return list(filter(self.in_board, [
            point + SegmentDirection.X, point - SegmentDirection.X,
            point + SegmentDirection.Y, point - SegmentDirection.Y
        ]))

    def in_board_grid(self, point: Coordinate) -> bool:
        return 0 <= point.x < self.width and 0 <= point.y < self.height

    def is_connected(self, pos: SegmentPos) -> bool:
        return pos not in self.segments or self.segments[pos].connected

    def check(self, path: Path) -> bool:
        return (all(point.check(self, pos, path) for pos, point in self.points.items())
                and all(segment.check(self, pos, path) for pos, segment in self.segments.items())
                and all(grid.check(self, pos, path) for pos, grid in self.grids.items()))

    def connect(self, pos: SegmentPos) -> None:
        self.segments[pos].connected = True

    def disconnect(self, pos: SegmentPos) -> None:
        self.segments[pos].connected = False

    def add_point_shape(self, x: int, y: int, shape: Shape) -> None:
        self.points[Coordinate(x, y)].shapes.append(shape)

    def add_segment_shape(self, pos: SegmentPos, shape: Shape) -> None:
        self.segments[pos].shapes.append(shape)

    def add_grid_shape(self, x: int, y: int, shape: Shape) -> None:
        self.grids[Coordinate(x, y)].shapes.append(shape)

    def find_including_part(self, grid: Coordinate, path: Path) -> BoardPart:
        grids: set[Coordinate] = set()

        def finder(current: Coordinate, found: list[Coordinate] | None = None) -> None:
            if found is None:
                found = []
            grids.add(current)
            for d1, d2 in ((SegmentDirection.X, SegmentDirection.Y), (SegmentDirection.Y, SegmentDirection.X)):
                if self.in_board_grid(near := current + d1) and SegmentPos(current + d1, d2) not in path.segments:
                    if near not in found:
                        finder(near, found + [current])
                if self.in_board_grid(near := current - d1) and SegmentPos(current, d2) not in path.segments:
                    if near not in found:
                        finder(near, found + [current])

        finder(grid)
        return BoardPart(grids)
