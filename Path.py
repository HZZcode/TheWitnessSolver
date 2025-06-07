from Position import Coordinate, SegmentPos
from multipledispatch import dispatch
from typing import TYPE_CHECKING, Self

if TYPE_CHECKING:
    from Board import Board


class Path:
    points: list[Coordinate]
    goal: Coordinate

    @property
    def segments(self) -> list[SegmentPos]:
        return [SegmentPos.between(p, q) for p, q in zip(self.points[:-1], self.points[1:])]

    @dispatch(Coordinate, Coordinate)
    def __init__(self, start: Coordinate, goal: Coordinate):
        self.__init__([start], goal)

    @dispatch(list, Coordinate)
    def __init__(self, points: list[Coordinate], goal: Coordinate):
        self.points = points
        self.goal = goal

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        points_str: str = '->'.join(map(str, self.points))
        if self.points[-1] == self.goal:
            return points_str
        return points_str + '->...->' + str(self.goal)

    def __add__(self, point: Coordinate) -> Self:
        return Path(self.points + [point], self.goal)


def find_paths(board: 'Board') -> list[Path]:
    goal: Coordinate = board.end_point
    paths: list[Path] = []

    def finder(current: Path) -> None:
        last: Coordinate = current.points[-1]
        if last == goal:
            if board.check(current):
                paths.append(current)
            return
        for near in board.nears(last):
            if near not in current.points and board.is_connected(SegmentPos.between(last, near)):
                finder(current + near)

    finder(Path(board.start_point, goal))
    return paths
