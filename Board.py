from copy import deepcopy
from dataclasses import dataclass, field
from typing import Self, Generator

from DefaultedDict import DefaultedDict
from Position import Coordinate, SegmentPos, Position, SegmentDirection, BoardPart
from Shape import Shape, Jack
from Path import Path


@dataclass
class BoardObject:
    shapes: list[Shape] = field(default_factory=list)

    def __post_init__(self):
        if self.shapes is None:
            self.shapes = []

    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        return all(shape.check(board, pos, path) for shape in self.shapes)

    def without_one_shape(self) -> Generator[Self, None, None]:
        for i in range(len(self.shapes)):
            copied = deepcopy(self)
            copied.shapes.remove(copied.shapes[i])
            yield copied

    def without_jack(self) -> Self:
        copied = deepcopy(self)
        copied.shapes.remove([shape for shape in copied.shapes if isinstance(shape, Jack)][0])
        return copied


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

    def with_grid(self, pos: Coordinate, grid: Grid) -> Self:
        copied = deepcopy(self)
        copied.grids[pos] = grid
        return copied

    def with_segment(self, pos: SegmentPos, segment: Segment) -> Self:
        copied = deepcopy(self)
        copied.segments[pos] = segment
        return copied

    def with_point(self, pos: Coordinate, point: Point) -> Self:
        copied = deepcopy(self)
        copied.points[pos] = point
        return copied

    def diff_jack(self, path: Path, jack_pos: Coordinate) -> list[tuple[Self, Self]]:
        no_jack = self.with_grid(jack_pos, self.grids[jack_pos].without_jack())
        part = self.find_including_part(jack_pos, path)
        diff_grid = [(no_jack.with_grid(grid, changed), no_jack)
                for grid in part.grids
                if grid != jack_pos
                for changed in self.grids[grid].without_one_shape()]
        diff_segment = [(no_jack.with_segment(segment, changed), no_jack)
                for segment in part.segments
                if segment not in path.segments
                for changed in self.segments[segment].without_one_shape()]
        diff_point = [(no_jack.with_point(point, changed), no_jack)
                for point in part.points
                if point not in path.points
                for changed in self.points[point].without_one_shape()]
        return diff_grid + diff_segment + diff_point

    def check(self, path: Path) -> bool:
        jacks: list[Coordinate] = [pos for pos, grid in self.grids.items()
                                   if any(isinstance(shape, Jack) for shape in grid.shapes)]
        if len(jacks) != 0:
            jack_pos = jacks[0]
            return any(changed[0].check(path) and not changed[1].check(path)
                       for changed in self.diff_jack(path, jack_pos))
        else:
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
