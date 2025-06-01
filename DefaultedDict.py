def DefaultedDict(TKey: type, TValue: type) -> type:
    class Cls(dict[TKey, TValue]):
        def __init__(self) -> None:
            super().__init__()

        def __getitem__(self, key: TKey) -> TValue:
            if key not in self:
                self[key] = TValue()
            return super().__getitem__(key)

        # __getitem__ method might change dict size, so we have to copy before getting iterator to avoid error

        def __iter__(self):
            return iter(self.copy())

        def values(self):
            return self.copy().values()

        def items(self):
            return self.copy().items()

    return Cls
