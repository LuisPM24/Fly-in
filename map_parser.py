from arguments import Arguments
from map_components import Hub, Connection
from typing import Any


class MapParser:
    """
    Parses and generates a valid map
    """
    def __init__(self, selected_map: str = "",
                 visual_representation: str = "") -> None:
        arguments = Arguments(selected_map, visual_representation)

        self.map: str = arguments.selected_map
        self.visual: str = arguments.visual_representation
        self.nb_drones: int | None = None
        self.start_hub: Hub | None = None
        self.end_hub: Hub | None = None
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.connection_keys: set[frozenset[str]] = set()
        self.parse_map()

    def parse_map(self) -> None:
        """
        Gets all data from the selected map
        """
        with open(self.map, "r") as file:
            for line_number, line in enumerate(file, start=1):
                if (line.startswith("#") or line.isspace()):
                    continue

                if line.startswith("nb_drones:"):
                    if self.nb_drones is None:
                        self.nb_drones = self.parse_nb_drones(line,
                                                              line_number)
                        continue
                    else:
                        raise ValueError(f"(Line {line_number}) Two or more"
                                         " nb_drones definitions")
                elif self.nb_drones is None:
                    raise ValueError(f"(Line {line_number}) nb_drones must"
                                     " be first line")

                if line.startswith("start_hub:"):
                    if self.start_hub is not None:
                        raise ValueError(f"(Line {line_number}) Two or more"
                                         " start_hub definitions")
                    new_hub: Hub = self.parse_hub("start_hub:", line,
                                                  line_number)
                    self.add_hub(new_hub, line_number)
                    self.start_hub = new_hub
                elif line.startswith("end_hub:"):
                    if self.end_hub is not None:
                        raise ValueError(f"(Line {line_number}) Two or more"
                                         "end_hub definitions")
                    new_hub = self.parse_hub("end_hub:", line, line_number)
                    self.add_hub(new_hub, line_number)
                    self.end_hub = new_hub
                elif line.startswith("hub:"):
                    new_hub = self.parse_hub("hub:", line, line_number)
                    self.add_hub(new_hub, line_number)
                elif line.startswith("connection:"):
                    new_connection: Connection = (
                        self.parse_connection(line, line_number)
                        )
                    self.connections.append(new_connection)
                else:
                    raise ValueError(f"(Line {line_number}) Invalid line at"
                                     f" map definition: {line}")

        if self.start_hub is None:
            raise ValueError("No start_hub at map definition")
        elif self.end_hub is None:
            raise ValueError("No end_hub at map definition")

    def add_hub(self, hub: Hub, line_number: int) -> None:
        """
        Adds a Hub class to the internal map dictionary
        """
        if hub.name in self.hubs:
            raise ValueError(f"(Line {line_number}) Two or more hubs with the"
                             f" same name: '{hub.name}'")
        self.hubs[hub.name] = hub

    def parse_hub(self, to_search: str, line: str, line_number: int) -> Hub:
        """
        Parse and returns a Hub class
        """
        if not line:
            raise ValueError(f"(Line {line_number}) Invalid line: '{line}'")

        new_line = line.replace(to_search, "", 1)
        words = new_line.split()

        if len(words) < 3:
            raise ValueError(f"(Line {line_number}) Invalid line: '{line}'")

        is_start: bool = False
        is_end: bool = False

        if to_search == "start_hub:":
            is_start = True
        elif to_search == "end_hub:":
            is_end = True

        name: str = words[0]
        x_value: int = int(words[1])
        y_value: int = int(words[2])
        properties: dict[str, Any] = {}

        if len(words) > 3:
            properties = self.validate_hub_properties(line, words[3:],
                                                      line_number)

        return Hub(is_start, is_end, name, x_value, y_value, properties)

    def validate_hub_properties(self, line: str, properties: list[str],
                                line_number: int) -> dict[str, Any]:
        """
        Validates hub metadata. Returns a dictionary with all
        info from the Hub.
        """
        if not properties:
            return {}

        properties_text: str = " ".join(properties)

        if (not properties_text.startswith("[") or
           not properties_text.endswith("]")):
            raise ValueError(f"(Line {line_number}) Invalid properties format"
                             f" for line: '{line.strip()}'")

        properties_text = properties_text[1:-1].strip()

        if not properties_text:
            raise ValueError(f"(Line {line_number}) Empty properties block for"
                             f" line: '{line.strip()}'")

        if "[" in properties_text or "]" in properties_text:
            raise ValueError(f"(Line {line_number}) Invalid properties format"
                             f" for line: '{line.strip()}'")

        result: dict[str, Any] = {}

        for metadata in properties_text.split():
            if metadata.count("=") != 1:
                raise ValueError(f"(Line {line_number}) Invalid metadata"
                                 f" '{metadata}'")

            key, value = metadata.split("=", 1)

            if not key or not value:
                raise ValueError(f"(Line {line_number}) Invalid metadata"
                                 f" '{metadata}'")
            elif key in result:
                raise ValueError(f"(Line {line_number}) Duplicate metadata"
                                 f" '{key}'")
            elif key == "max_drones":
                try:
                    result[key] = int(value)
                except ValueError:
                    raise ValueError(f"(Line {line_number}) Invalid max_drones"
                                     f"value: '{value}'")
            else:
                result[key] = value

        return result

    def get_hub(self, name: str, line_number: int) -> Hub:
        """
        Search and return a Hub class
        """
        if name not in self.hubs:
            raise ValueError(f"(Line {line_number}) Hub not found: '{name}'")
        return self.hubs[name]

    def parse_connection(self, line: str, line_number: int) -> Connection:
        """
        Parse and returns a connection class
        """
        new_line: str = line.replace("connection:", "", 1)
        words: list[str] = new_line.split()

        if len(words) == 0 or len(words) > 2:
            raise ValueError(f"(Line {line_number}) Invalid connection")

        points: list[str] = words[0].split("-")
        connection_key: frozenset[str] = frozenset([points[0], points[1]])

        if connection_key in self.connection_keys:
            raise ValueError(f"(Line {line_number}) Duplicate connection")

        if len(points) != 2 or not points[0] or not points[1]:
            raise ValueError(f"(Line {line_number}) Invalid connection")

        point_a: Hub = self.get_hub(points[0], line_number)
        point_b: Hub = self.get_hub(points[1], line_number)
        capacity: int = 1

        if len(words) == 2:
            capacity = self.parse_connection_properties(words[1], line_number)

        self.connection_keys.add(connection_key)

        return Connection(point_a, point_b, capacity)

    def parse_connection_properties(self, metadata: str,
                                    line_number: int) -> int:
        """
        Parse all metadata from a Connection class
        """
        if (not metadata.startswith("[") or
           not metadata.endswith("]")):
            raise ValueError(f"(Line {line_number}) Invalid connection "
                             "metadata format")

        metadata = metadata[1:-1]

        if metadata.count("=") != 1:
            raise ValueError(f"(Line {line_number}) Invalid connection"
                             f"metadata: '{metadata}'")

        key, value = metadata.split("=", 1)

        if key != "max_link_capacity":
            raise ValueError(f"(Line {line_number}) Invalid connection"
                             f" metadata: '{key}'")

        try:
            capacity: int = int(value)
        except ValueError:
            raise ValueError(f"(Line {line_number}) Invalid max_link_capacity:"
                             f" '{value}'")

        if capacity <= 0:
            raise ValueError(f"(Line {line_number}) Invalid max_link_capacity:"
                             f" '{value}'")

        return capacity

    def get_connections(self, name: str) -> list[Connection]:
        """
        Returns all related connections to a Hub name
        """
        if name not in self.hubs:
            raise ValueError(f"Invalid hub: '{name}'")

        return_value: list[Connection] = []

        for conn in self.connections:
            if conn.pointA.name or conn.pointB.name is name:
                return_value.append(conn)

        return return_value

    def parse_nb_drones(self, line: str, line_number: int) -> int:
        """
        Validates and return the amount of nb_drones marked in the map
        """
        if not line:
            raise ValueError(f"(Line {line_number}) Invalid line")

        new_line = line.replace("nb_drones:", "", 1)
        words = new_line.split()

        if len(words) != 1:
            raise ValueError(f"(Line {line_number}) Invalid nb_drones"
                             " declaration")

        drones: int = int(words[0])

        if drones <= 0:
            raise ValueError(f"(Line {line_number}) Invalid nb_drones"
                             f" declaration: {line}")

        return drones
