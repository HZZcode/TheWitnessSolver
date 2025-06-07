import random
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from itertools import combinations
from typing import Generator

from Board import Board
from Path import Path, find_paths
from Position import Position, is_point, is_segment, Coordinate, SegmentPos, is_grid
from Shape import Hexagon, Colors, Square, ColorType, Block, Star, Triangle


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
        colors = board.get_colors_in(self.position, solution)
        color = random.choice(list(Colors)) if len(colors) == 0 else colors[0]
        board.add_grid_shape(self.position.x, self.position.y, Square(color))


@dataclass
class GridAddBlockAction(Action):
    position: Coordinate

    def apply_on(self, board: Board, solution: Path) -> None:
        part = board.find_including_part(self.position, solution).rotatable()
        board.add_grid_shape(self.position.x, self.position.y, Block(part))


@dataclass
class GridFixBlockAction(Action):
    position: Coordinate

    def apply_on(self, board: Board, solution: Path) -> None:
        for shape in board.grids[self.position].shapes:
            if isinstance(shape, Block):
                shape.shape.rotate = False


@dataclass
class GridSplitBlockAction(Action):
    position: Coordinate
    split_positions: tuple[Coordinate, Coordinate]
    block: Block

    def apply_on(self, board: Board, solution: Path) -> None:
        parts = self.block.shape.split()
        board.grids[self.position].shapes.remove(self.block)
        for i in [0, 1]:
            board.add_grid_shape(self.split_positions[i].x, self.split_positions[i].y, Block(parts[i]))


@dataclass
class GridSingleStarAction(Action):
    position: Coordinate
    color: ColorType

    def apply_on(self, board: Board, solution: Path) -> None:
        board.add_grid_shape(self.position.x, self.position.y, Star(self.color))


@dataclass
class GridDoubleStarAction(Action):
    positions: tuple[Coordinate, Coordinate]

    def apply_on(self, board: Board, solution: Path) -> None:
        colors = board.get_colors_in(self.positions[0], solution)
        unused = set(Colors) - set(colors)
        color = random.choice(list(unused))
        for i in [0, 1]:
            board.add_grid_shape(self.positions[i].x, self.positions[i].y, Star(color))


@dataclass
class GridTriangleAction(Action):
    position: Coordinate

    def apply_on(self, board: Board, solution: Path) -> None:
        segment_count = board.get_segment_count(self.position, solution)
        board.add_grid_shape(self.position.x, self.position.y, Triangle(segment_count))


def get_actions_on(board: Board, pos: Position, solution: Path) -> Generator[Action, None, None]:
    if is_point(pos):
        if (pos in solution.points and pos not in [board.start_point, board.end_point]
                and not any(isinstance(shape, Hexagon) for shape in board.points[pos].shapes)):
            yield PointHexagonAction(pos)
    if is_segment(pos):
        if pos not in solution.segments and board.segments[pos].connected:
            yield SegmentDisconnectAction(pos)
    if is_grid(pos):
        grid = board.grids[pos]
        grids: set[Coordinate] = board.find_including_part(pos, solution).grids
        colors: list[ColorType] = board.get_colors_in(pos, solution)
        random.shuffle(colors)
        single_colors: list[ColorType] = [color for color in colors if colors.count(color) == 1]
        spaces: set[Coordinate] = {grid for grid in grids if len(board.grids[grid].shapes) == 0}
        if len(grid.shapes) == 0:
            if board.get_segment_count(pos, solution) != 0:
                yield GridTriangleAction(pos)
            if len(set(colors)) <= 1:
                yield GridSquareAction(pos)
            if not any(isinstance(shape, Block) for grid in grids for shape in board.grids[grid].shapes):
                yield GridAddBlockAction(pos)
            if len(set(colors)) < len(list(Colors)):
                for combination in combinations(spaces.union({pos}), 2):
                    yield GridDoubleStarAction(combination)
            for color in single_colors:
                for space in spaces:
                    yield GridSingleStarAction(space, color)
        else:
            shape = grid.shapes[0]
            if isinstance(shape, Block):
                yield GridFixBlockAction(pos)
                for combination in combinations(spaces.union({pos}), 2):
                    yield GridSplitBlockAction(pos, combination, shape)


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

    def trim_shapes(modified: Board) -> Generator[Board, None, None]:
        if len(find_paths(modified)) != 1:
            return
        for container in [modified.points, modified.segments, modified.grids]:
            deletable = [key for key in container.keys() if container[key].is_default()]
            for key in deletable:
                del container[key]
        trims = [trimmed for trimmed in modified.without_one_shape() if len(find_paths(trimmed)) == 1]
        if len(trims) == 0:
            yield modified
        else:
            for trimmed in trims:
                yield from trim_shapes(trimmed)

    for found in finder(deepcopy(board)):
        yield from trim_shapes(found)


def generate_part(board: Board, solution: Path, count: int) -> Generator[Board, None, None]:
    for _ in range(count):
        for generated in generate(board, solution):
            yield generated
            break
