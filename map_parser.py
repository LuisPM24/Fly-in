from arguments import Arguments
from map_components import Hub, Connection
from typing import Any


class MapParser:
    def __init__(self, selected_map: str = "",
                 visual_representation: str = "") -> None:
        arguments = Arguments(selected_map, visual_representation)

        self.map: str = arguments.selected_map
        self.visual: str = arguments.visual_representation
        self.start_hub: Hub | None = None
        self.end_hub: Hub | None = None
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        # self.validate_hubs()
        self.parse_map()

    def parse_map(self) -> None:
        with open(self.map, "r") as file:
            for line in file:
                if (line.startswith("#") or line.startswith("nb_drones:")
                   or line.isspace()):
                    continue

                if line.startswith("start_hub:"):
                    if self.start_hub is not None:
                        raise ValueError("Two or more start_hub definitions")
                    new_hub: Hub = self.parse_hub("start_hub:", line)
                    self.add_hub(new_hub)
                    self.start_hub = new_hub
                elif line.startswith("end_hub:"):
                    if self.end_hub is not None:
                        raise ValueError("Two or more end_hub definitions")
                    new_hub = self.parse_hub("end_hub:", line)
                    self.add_hub(new_hub)
                    self.end_hub = new_hub
                elif line.startswith("hub:"):
                    new_hub = self.parse_hub("hub:", line)
                    self.add_hub(new_hub)
                elif line.startswith("connection:"):
                    new_connection: Connection = (self.parse_connection(line))
                    self.connections.append(new_connection)
                else:
                    raise ValueError(f"Invalid line at map definition: {line}")

        if self.start_hub is None:
            raise ValueError("No start_hub at map definition")
        elif self.end_hub is None:
            raise ValueError("No end_hub at map definition")

    def add_hub(self, hub: Hub) -> None:
        if hub.name in self.hubs:
            raise ValueError(
                f"Two or more hubs with the same name: '{hub.name}'")
        self.hubs[hub.name] = hub

    def parse_hub(self, to_search: str, line: str) -> Hub:
        if not line:
            raise ValueError(f"Invalid line: '{line}'")

        new_line = line.replace(to_search, "", 1)
        words = new_line.split()

        if len(words) < 3:
            raise ValueError(f"Invalid line: '{line}'")

        is_start: bool = False
        is_end: bool = False

        if to_search == "start_hub:":
            is_start = True
        elif to_search == "end_hub:":
            is_end = True

        try:
            name: str = words[0]
            x_value: int = int(words[1])
            y_value: int = int(words[2])
            properties: dict[str, Any] = {}

            if len(words) > 3:
                properties = self.validate_hub_properties(line, words[3:])

            return Hub(is_start, is_end, name, x_value, y_value, properties)
        except ValueError as e:
            raise ValueError(e)

    def validate_hub_properties(self, line: str, properties: list[str]
                                ) -> dict[str, Any]:
        if not properties:
            return {}

        properties_text: str = " ".join(properties)

        if (not properties_text.startswith("[") or
           not properties_text.endswith("]")):
            raise ValueError("Invalid properties format for line: "
                             f"'{line.strip()}'")

        properties_text = properties_text[1:-1].strip()

        if not properties_text:
            raise ValueError("Empty properties block for line: "
                             f"'{line.strip()}'")

        if "[" in properties_text or "]" in properties_text:
            raise ValueError("Invalid properties format for line: "
                             f"'{line.strip()}'")

        result: dict[str, Any] = {}

        for metadata in properties_text.split():
            if metadata.count("=") != 1:
                raise ValueError(f"Invalid metadata '{metadata}'")

            key, value = metadata.split("=", 1)

            if not key or not value:
                raise ValueError(f"Invalid metadata '{metadata}'")
            elif key in result:
                raise ValueError(f"Duplicate metadata '{key}'")
            elif key == "max_drones":
                try:
                    result[key] = int(value)
                except ValueError:
                    raise ValueError("Invalid max_drones value: "
                                     f"'{value}'")
            else:
                result[key] = value

        return result

    def get_hub(self, name: str) -> Hub:
        if name not in self.hubs:
            raise ValueError(f"Hub not found: '{name}'")
        return self.hubs[name]

    def parse_connection(self, line: str) -> Connection:
        new_line: str = line.replace("connection:", "", 1)
        words: list[str] = new_line.split()

        if len(words) == 0 or len(words) > 2:
            raise ValueError(f"Invalid connection in line: '{line.strip()}'")

        points: list[str] = words[0].split("-")

        if len(points) != 2 or not points[0] or not points[1]:
            raise ValueError(f"Invalid connection in line: '{line.strip()}'")

        point_a: Hub = self.get_hub(points[0])
        point_b: Hub = self.get_hub(points[1])
        capacity: int = 1

        if len(words) == 2:
            capacity = self.parse_connection_properties(words[1], line)

        return Connection(point_a, point_b, capacity)

    def parse_connection_properties(self, metadata: str, line: str) -> int:
        if (not metadata.startswith("[") or
           not metadata.endswith("]")):
            raise ValueError("Invalid connection metadata format in line: "
                             f"'{line.strip()}'")

        metadata = metadata[1:-1]

        if metadata.count("=") != 1:
            raise ValueError(f"Invalid connection metadata: '{metadata}'")

        key, value = metadata.split("=", 1)

        if key != "max_link_capacity":
            raise ValueError(f"Invalid connection metadata: '{key}'")

        try:
            capacity: int = int(value)
        except ValueError:
            raise ValueError(f"Invalid max_link_capacity: '{value}'")

        if capacity <= 0:
            raise ValueError(f"Invalid max_link_capacity: '{value}'")

        return capacity
