from arguments import Arguments
from map_components import Hub


class MapParser:
    def __init__(self, selected_map: str = "",
                 visual_representation: str = "") -> None:
        arguments = Arguments(selected_map, visual_representation)

        self.map: str = arguments.selected_map
        self.visual: str = arguments.visual_representation
        self.start_hub: Hub | None = None
        self.end_hub: Hub | None = None
        self.hubs: dict[str, Hub] = {}
        # self.connections: list[connection] = []
        # self.validate_hubs()
        self.get_hubs()
        print(list(self.hubs))

    def get_hubs(self) -> None:
        with open(self.map, 'r') as file:
            for line in file:
                if (line.startswith("#") or line.startswith("nb_drones:")
                   or line.startswith("connection:") or line.isspace()):
                    continue
                elif line.startswith("start_hub:"):
                    if self.start_hub is not None:
                        raise ValueError("Two or more start_hub definitions")

                    new_hub: Hub = self.get_hub("start_hub:", line)
                    self.add_hub(new_hub)
                    self.start_hub = new_hub

                elif line.startswith("end_hub:"):
                    if self.end_hub is not None:
                        raise ValueError("Two or more end_hub definitions")

                    new_hub = self.get_hub("end_hub:", line)
                    self.add_hub(new_hub)
                    self.end_hub = new_hub

                elif line.startswith("hub:"):
                    new_hub = self.get_hub("hub:", line)
                    self.add_hub(new_hub)
                else:
                    raise ValueError(f"Invalid line at map definition: {line}")

            if self.start_hub is None:
                raise ValueError("No start_hub at map definition")
            if self.end_hub is None:
                raise ValueError("No end_hub at map definition")

    def add_hub(self, hub: Hub) -> None:
        if hub.name in self.hubs:
            raise ValueError(
                f"Two or more hubs with the same name: '{hub.name}'")
        self.hubs[hub.name] = hub

    def get_hub(self, to_search: str, line: str) -> Hub:
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

            return Hub(is_start, is_end, name, x_value, y_value)
        except ValueError as e:
            raise ValueError(e)
