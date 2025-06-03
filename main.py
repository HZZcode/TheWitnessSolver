from Board import Board
from Path import find_paths
from Position import Coordinate, BoardPart
from Shape import Block


def main() -> None:
    board = Board(2, 2, Coordinate(0, 0), Coordinate(2, 2))
    board.add_grid_shape(0, 0, Block(BoardPart.from_str([' #', '##', '##'])))
    board.add_grid_shape(1, 0, Block(BoardPart.from_str(['#'], negative=True)))
    board.add_grid_shape(1, 1, Block(BoardPart.from_str(['#'], negative=True)))
    paths = find_paths(board)
    for path in paths:
        print(path)
    print(f'Found {len(paths)} paths')


if __name__ == "__main__":
    main()
