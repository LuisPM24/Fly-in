from arguments import Arguments
from map_components import Hub


class MapParser:
    def __init__(self, selected_map: str = "",
                 visual_representation: str = "") -> None:
        arguments = Arguments(selected_map, visual_representation)

        self.map: str = arguments.selected_map
        self.visual: str = arguments.visual_representation
        self.starthub: Hub | None = None
        self.endhub: Hub | None = None
        self.hubs: list[Hub] = []
        # self.connections: list[connection] = []
        # self.validate_hubs()
        self.get_hubs()

    def get_hubs(self) -> None:
        with open(self.map, 'r') as file:
            for line in file:
                if line.startswith("#"):
                    continue
                if line.startswith("start_hub:"):
                    self.get_starthub(line)

    def get_starthub(self, line: str) -> None:
        if not line:
            return
        line = line.replace("start_hub:", "", 1)
        print(line)
