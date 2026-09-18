from typing import Any


class Hub:
    def __init__(self, is_start: bool = False, is_end: bool = False,
                 name: str = "", x: int = 0, y: int = 0,
                 properties: dict[str, Any] | None = None,) -> None:
        self.is_start: bool = is_start
        self.is_end: bool = is_end
        self.name = name
        self.x = x
        self.y = y
        self.properties: dict[str, Any] = (properties if
                                           properties is not None else {})

        self.validate_hub()

    def validate_hub(self) -> None:
        if self.is_start and self.is_end:
            raise ValueError("A hub can't be 'start_hub' and 'end_hub' "
                             "at the same time")

        if not self.name or "-" in self.name or " " in self.name:
            raise ValueError(f"Invalid name: '{self.name}'")

        valid_properties: set[str] = {
            "zone",
            "color",
            "max_drones",
        }

        for prop, value in self.properties.items():
            if prop not in valid_properties:
                raise ValueError(f"Invalid metadata '{prop}' at "
                                 f"'{self.name}' hub")

            if prop == "zone":
                self.validate_zone(value)
            elif prop == "color":
                self.validate_color(value)
            elif prop == "max_drones":
                self.validate_max_drones(value)

    def validate_zone(self, value: Any) -> None:
        valid_zones: set[str] = {
            "normal",
            "blocked",
            "restricted",
            "priority"
        }

        if not isinstance(value, str) or value not in valid_zones:
            raise ValueError(f"Invalid zone '{value}' at '{self.name}' hub")

    def validate_color(self, value: Any) -> None:
        valid_colors: set[str] = {
            "green",
            "blue",
            "yellow",
            "red",
            "pink",
            "purple"
        }

        if (not isinstance(value, str) or
           not value or any(char.isspace() for char in value) or
           value not in valid_colors):
            raise ValueError(f"Invalid color '{value}' at '{self.name}' hub")

        if not value or any(char.isspace() for char in value):
            raise ValueError(f"Invalid color '{value}' at '{self.name}' hub")

    def validate_max_drones(self, value: Any) -> None:
        if self.is_start or self.is_end:
            return

        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"Invalid max_drones '{value}' at "
                             f"'{self.name}' hub")

        if value <= 0:
            raise ValueError(f"Invalid max_drones '{value}' at "
                             f"'{self.name}' hub")
