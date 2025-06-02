from Board import Board
from Path import find_paths
from Position import Coordinate
from Shape import Hexagon, Jack


def main() -> None:
    board = Board(2, 2, Coordinate(0, 0), Coordinate(2, 2))
    board.add_point_shape(1, 1, Hexagon())
    board.add_grid_shape(0, 0, Jack())
    paths = find_paths(board)
    for path in paths:
        print(path)
    print(f'Found {len(paths)} paths')


if __name__ == "__main__":
    main()
