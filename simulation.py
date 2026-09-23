from map_parser import MapParser
from map_components import Connection


class Simulation:
    """
    Creates the Simulation class and launch a simulation via terminal,
    graphical or both
    """
    def __init__(self, map: MapParser) -> None:
        self.map = map

        if not map:
            raise ValueError("Invalid map for Simulation class")

        self.graph = self.get_graph()
        # self.launch

    def get_graph(self) -> dict[str, list[Connection]]:
        """
        Generates a Hub-Connection graph
        """
        return_value: dict[str, list[Connection]] = {}

        for name in self.map.hubs:
            values: list[Connection] = self.map.get_connections(name)
            return_value[name] = values

        return return_value
