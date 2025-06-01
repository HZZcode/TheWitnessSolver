from Board import Board
from Path import find_paths
from Position import Coordinate, SegmentPos
from Shape import Hexagon


def main() -> None:
    board = Board(2, 2, Coordinate(0, 0), Coordinate(2, 2))
    board.add_point_shape(0, 2, Hexagon())
    board.add_point_shape(1, 1, Hexagon())
    board.add_segment_shape(SegmentPos.between(2, 0, 2, 1), Hexagon())
    board.disconnect(SegmentPos.between(0, 0, 1, 0))
    paths = find_paths(board)
    for path in paths:
        print(path)
    print(f'Found {len(paths)} paths')


if __name__ == "__main__":
    main()
