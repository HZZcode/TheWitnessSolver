from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from Position import Position
from Path import Path

if TYPE_CHECKING:
    from Board import Board


class Shape(ABC):
    @abstractmethod
    def check(self, board: 'Board', pos: Position, path: Path) -> bool:
        ...
