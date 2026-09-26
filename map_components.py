from typing import Any


class Hub:
    def __init__(self, is_start: bool = False, is_end: bool = False,
                 name: str = "", x: int = 0, y: int = 0,
                 properties: dict[str, Any] | None = None,
                 line_number: int = 0) -> None:
        self.is_start: bool = is_start
        self.is_end: bool = is_end
        self.name = name
        self.x = x
        self.y = y
        self.properties: dict[str, Any] = {
            "zone": "normal",
            "color": "none",
            "max_drones": 1,
        }
        self.declaration_line: int = line_number

        if line_number == 0:
            raise ValueError("Error at Hub creation")

        if properties is not None:
            self.properties.update(properties)

        self.validate_hub()

    def validate_hub(self) -> None:
        if self.is_start and self.is_end:
            raise ValueError(f"(Line {self.declaration_line}) A hub can't be"
                             "'start_hub' and 'end_hub' at the same time")

        if not self.name or "-" in self.name or " " in self.name:
            raise ValueError(f"(Line {self.declaration_line}) Invalid name: "
                             f"'{self.name}'")

        valid_properties: set[str] = {
            "zone",
            "color",
            "max_drones",
        }

        for prop, value in self.properties.items():
            if prop not in valid_properties:
                raise ValueError(f"(Line {self.declaration_line}) Invalid "
                                 f"metadata '{prop}' at '{self.name}' hub")

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
            raise ValueError(f"(Line {self.declaration_line}) Invalid zone "
                             f"'{value}' at '{self.name}' hub")

    def validate_color(self, value: Any) -> None:
        if (not isinstance(value, str) or
           not value or any(char.isspace() for char in value)):
            raise ValueError(f"(Line {self.declaration_line}) Invalid color "
                             f"'{value}' at '{self.name}' hub")

    def validate_max_drones(self, value: Any) -> None:
        if self.is_start or self.is_end:
            return

        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"(Line {self.declaration_line}) Invalid "
                             f"max_drones '{value}' at '{self.name}' hub")

        if value <= 0:
            raise ValueError(f"(Line {self.declaration_line}) Invalid "
                             f"max_drones '{value}' at '{self.name}' hub")

    def get_movement_cost(self) -> int:
        zone: str = self.properties["zone"]

        if zone == "restricted":
            return 2
        return 1


class Connection:
    def __init__(self, pointA: Hub, pointB: Hub, capacity: int,
                 declaration_line: int) -> None:
        self.pointA = pointA
        self.pointB = pointB
        self.capacity = capacity
        self.declaration_line = declaration_line

        if self.capacity <= 0:
            raise ValueError(f"(Line {self.declaration_line}) Invalid capacity"
                             f" for connection between '{pointA.name}'-'"
                             f"{pointB.name}'")

    def get_hub(self, name: str) -> Hub:
        """
        Returns the indicated name hub
        """
        if self.pointA.name == name:
            return self.pointA
        elif self.pointB.name == name:
            return self.pointB
        else:
            raise ValueError(f"(Line {self.declaration_line}) Invalid name at "
                             f"'get_hub' function: {name}")

    def get_zone(self, name: str) -> str:
        """
        Returns the zone type
        """
        hub: Hub = self.get_hub(name)
        return hub.properties["zone"]

    def get_opposite_hub(self, name: str) -> Hub:
        """
        Returns the opposite hub to the indicated
        """
        if self.pointA.name == name:
            return self.pointB
        elif self.pointB.name == name:
            return self.pointA
        else:
            raise ValueError(f"(Line {self.declaration_line}) Invalid name at "
                             f"'get_opposite_hub' function: '{name}'")
