# TheWitnessSolver

A solver and puzzle generator for [The Witness](https://en.wikipedia.org/wiki/The_Witness_(2016_video_game)) line puzzles, in pure Python.

- The **solver** enumerates every valid path from the start point to the end point on a board with symbols.
- The **generator** takes a board and an intended solution, decorates the board with symbols step by step, and keeps a board only when the intended solution is its **unique** solution — then trims away every symbol whose removal preserves uniqueness. The result is a minimal puzzle guaranteed to have exactly the solution you designed.

## Supported puzzle elements

| Element | Rule (as implemented) |
|---|---|
| Hexagon | The path must pass through the marked point or segment. |
| Colored square | All squares inside one region must share a single color. |
| Polyomino block | Each region must be exactly tiled by the blocks it contains. Blocks may be rotatable or fixed; negative (eraser) blocks are supported. |
| Star | Each region must contain exactly two objects of the star's color. |
| Triangle | The path must run along exactly *N* edges of the cell. |
| Jack (negative) | Cancels one other symbol in its region; the solver tries every possible removal. |
| Broken edge | The segment is removed from the grid and cannot be walked through. |

A *region* is a connected component of cells left when the drawn path is treated as walls.

## Usage

```python
from Board import Board
from Generator import generate_part
from Path import Path, find_paths
from Position import Coordinate

# A 2x2 board; the path starts at (0, 0) and ends at (2, 2).
board = Board(2, 2, Coordinate(0, 0), Coordinate(2, 2))
solution = Path([Coordinate(0, 0), Coordinate(0, 1), Coordinate(1, 1),
                 Coordinate(1, 2), Coordinate(2, 2)], Coordinate(2, 2))

# Decorate the board until `solution` becomes its unique solution
# (up to 10 generation attempts).
for puzzle in generate_part(board, solution, 10):
    print(find_paths(puzzle))   # -> exactly one path: `solution`
```

You can also place symbols manually and just solve:

```python
from Shape import Square

board.add_grid_shape(0, 0, Square("blue"))
board.add_grid_shape(1, 1, Square("red"))
paths = find_paths(board)   # every valid path on this board
```

Coordinates follow the game's convention: the lower-left cell is `(0, 0)`, and
points range over `[0, width] x [0, height]`.

## How it works

- **Solving** — depth-first enumeration of paths over the grid graph; each rule
  is checked against the regions induced by the candidate path
  (`Board.find_including_part`). Polyomino packing is decided by a recursive
  matcher over a small region-algebra (`BoardPart`: union, intersection,
  translation, rotation, negation).
- **Generating** — a randomized action sequence (place a symbol, split a block,
  disconnect an edge, ...). After every step the solver re-verifies that the
  intended solution is still unique; branches that break uniqueness are
  abandoned. A final `trim_shapes` pass removes redundant symbols while the
  solution stays unique.

## Requirements

- Python **3.12+** (PEP 695 generics / `type` aliases, `StrEnum`, `Self`)
- [`multipledispatch`](https://pypi.org/project/multipledispatch/) — `pip install multipledispatch`

## Notes

- This is a headless (no rendering) model of the game: boards and paths are
  plain Python objects, which makes them easy to feed into search or analysis
  code.
- Educational project — the rule set covers a large and useful subset of the
  game's panels, but not all of its mechanics.

## License

[MIT](LICENSE) © 2025 ZZ_404
