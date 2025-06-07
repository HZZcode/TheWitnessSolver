# I hate repr. Why not just default it to str instead of printing useless pointer address?
from typing import TypeVar

T = TypeVar('T', bound=type)


# I don't know why, but using `def no_repr(cls: type) -> type` puzzles the type checker


def no_repr(cls: T) -> T:
    def new_repr(self: T) -> str:
        if not hasattr(self, '__str__'):
            return object.__str__(self)
        try:
            return str(self)
        except RecursionError:
            return f"RecursionError encountered in __str__: {object.__repr__(self)}"

    cls.__repr__ = new_repr
    return cls
