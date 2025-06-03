def id_getter():
    current = 0
    def get_id() -> int:
        nonlocal current
        current += 1
        return current
    return get_id