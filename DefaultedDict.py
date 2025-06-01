def DefaultedDict(TKey: type, TValue: type) -> type:
    class Cls(dict[TKey, TValue]):
        def __init__(self) -> None:
            super().__init__()

        def __getitem__(self, key: TKey) -> TValue:
            if key not in self:
                self[key] = TValue()
            return super().__getitem__(key)
    return Cls
