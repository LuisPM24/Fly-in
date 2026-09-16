from typing import Any


class Hub:
    def __init__(self, is_start: bool = False, is_end: bool = False,
                 name: str = "", x: int = 0, y: int = 0,
                 properties: dict[str, Any] = {}) -> None:
        self.is_start = is_start
        self.is_end = is_end
        self.name = name
        self.x = x
        self.y = y
        self.properties = properties

        self.validate_hub()

    def validate_hub(self) -> None:
        if self.is_start and self.is_end:
            raise ValueError("A hub can't be 'start_hub' and 'end_hub'")
        if not self.name.isspace():
            raise ValueError("Invalid name")
        for prop in list(self.properties.keys()):
            if prop.isspace():
                raise ValueError(f"Invalid metadata at '{prop}' hub")
