import random
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from typing import Generator

from Board import Board
from Path import Path, find_paths
from Position import Position, is_point, is_segment, Coordinate, SegmentPos, is_grid
from Shape import Hexagon, Colored, Colors, Square, ColorType


class Action(ABC):
    @abstractmethod
    def apply_on(self, board: Board, solution: Path) -> None:
        ...


@dataclass
class PointHexagonAction(Action):
    position: Coordinate

    def apply_on(self, board: Board, solution: Path) -> None:
        board.add_point_shape(self.position.x, self.position.y, Hexagon())


@dataclass
class SegmentDisconnectAction(Action):
    position: SegmentPos

    def apply_on(self, board: Board, solution: Path) -> None:
        board.disconnect(self.position)


@dataclass
class GridSquareAction(Action):
    position: Coordinate

    def apply_on(self, board: Board, solution: Path) -> None:
        colors = [shape.color for grid in board.find_including_part(self.position, solution).grids
                  for shape in board.grids[grid].shapes if isinstance(shape, Colored)]
        color = random.choice(list(Colors)) if len(colors) == 0 else colors[0]
        board.add_grid_shape(self.position.x, self.position.y, Square(color))


@dataclass
class GridBlockAction(Action):
    position: Coordinate

    def apply_on(self, board: Board, solution: Path) -> None:
        ... # FIXME!


def get_actions_on(board: Board, pos: Position, solution: Path) -> Generator[Action, None, None]:
    if is_point(pos):
        if (pos in solution.points and pos not in [board.start_point, board.end_point]
                and not any(isinstance(shape, Hexagon) for shape in board.points[pos].shapes)):
            yield PointHexagonAction(pos)
    if is_segment(pos):
        if pos not in solution.segments and board.segments[pos].connected:
            yield SegmentDisconnectAction(pos)
    if is_grid(pos) and len(board.grids[pos].shapes) == 0:
        grids: set[Coordinate] = board.find_including_part(pos, solution).grids
        colors: set[ColorType] = {shape.color for grid in grids
                                  for shape in board.grids[grid].shapes
                                  if isinstance(shape, Colored)}
        spaces: set[Coordinate] = {grid for grid in grids if len(board.grids[grid].shapes) == 0}
        if len(set(colors)) <= 1:
            yield GridSquareAction(pos)


def get_actions(board: Board, solution: Path) -> list[Action]:
    return [action for pos in board.positions() for action in get_actions_on(board, pos, solution)]


def generate(board: Board, solution: Path) -> Generator[Board, None, None]:
    def finder(modified: Board) -> Generator[Board, None, None]:
        paths = find_paths(modified)
        if len(paths) == 0:
            return
        if len(paths) == 1:
            yield modified
            return
        actions: list[Action] = get_actions(modified, solution)
        random.shuffle(actions)
        for action in actions:
            copied = deepcopy(modified)
            action.apply_on(copied, solution)
            yield from finder(copied)

    return finder(deepcopy(board))


def generate_part(board: Board, solution: Path, count: int) -> Generator[Board, None, None]:
    for _ in range(count):
        for generated in generate(board, solution):
            yield generated
            break
