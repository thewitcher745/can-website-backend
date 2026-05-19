def parse_bool(value: str | None) -> bool | None:
    """Parses string to bool."""
    if not value:
        return None

    return value.lower() == "true"
