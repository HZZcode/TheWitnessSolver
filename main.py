from Board import Board
from Generator import generate_part
from Path import Path
from Position import Coordinate


def main() -> None:
    from pprint import pprint
    board = Board(2, 2, Coordinate(0, 0), Coordinate(2, 2))
    solution = Path([Coordinate(0, 0), Coordinate(0, 1), Coordinate(0, 2), Coordinate(1, 2), Coordinate(2, 2)],
                    Coordinate(2, 2))
    pprint(list(generate_part(board, solution, 10)))


if __name__ == "__main__":
    main()
