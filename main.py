from Board import Board
from Path import find_paths
from Position import Coordinate
from Shape import Triangle


def main() -> None:
    board = Board(2, 2, Coordinate(0, 0), Coordinate(2, 2))
    board.add_grid_shape(0, 0, Triangle(2))
    board.add_grid_shape(1, 0, Triangle(2))
    paths = find_paths(board)
    for path in paths:
        print(path)
    print(f'Found {len(paths)} paths')


if __name__ == "__main__":
    main()
