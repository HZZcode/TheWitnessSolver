from Board import Board, Segment
from Path import find_paths
from Position import Coordinate, SegmentPos, SegmentDirection


def main() -> None:
    board = Board(2, 2, Coordinate(0, 0), Coordinate(2, 2), segments={
        SegmentPos(Coordinate(0, 0), SegmentDirection.X): Segment().with_connected(False),
        SegmentPos(Coordinate(0, 1), SegmentDirection.Y): Segment().with_connected(False),
        SegmentPos(Coordinate(1, 1), SegmentDirection.X): Segment().with_connected(False),
    })
    for path in find_paths(board):
        print(path)


if __name__ == "__main__":
    main()
