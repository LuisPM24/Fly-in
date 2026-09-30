import heapq
from map_parser import MapParser
from map_components import Hub, Connection, Drone
from rich.console import Console
from rich.text import Text


class Simulation:
    """
    Creates the Simulation class and launches a simulation via terminal,
    graphical interface or both.
    """
    def __init__(self, map_parser: MapParser) -> None:
        self.map = map_parser
        self.graph: dict[str, list[Connection]] = self.get_graph()
        self.routes: list[tuple[list[str], int, int]] = []
        self.drones: list[Drone] = []

        if (self.map.start_hub is None or self.map.end_hub is None or
           self.map.nb_drones is None):
            raise ValueError("Invalid map for simulation")

        for route in self.yen(self.map.start_hub.name, self.map.end_hub.name,
                              10):
            self.routes.append((route, self.get_path_cost(route), 0))

        if not self.routes:
            raise ValueError("No route found between start and end")

        for drone_id in range(1, self.map.nb_drones + 1):
            route = self.assign_route()
            self.drones.append(Drone(drone_id, route,
                                     self.map.start_hub, self.map.end_hub))

        while self.check_simulation_end() is False:
            self.run_turn()

    def get_graph(self) -> dict[str, list[Connection]]:
        """
        Generates a Hub-Connection graph.
        """
        graph: dict[str, list[Connection]] = {}

        for name in self.map.hubs:
            graph[name] = self.map.get_connections(name)

        return graph

    def dijkstra(self, graph: dict[str, list[Connection]], start: str,
                 end: str, ignored_hubs: set[str] | None = None,
                 ignored_connections: set[frozenset[str]] | None = None
                 ) -> list[str]:
        """
        Searches the shortest path from start to end.
        """
        if start not in graph:
            raise ValueError(f"Invalid start hub: '{start}'")

        if end not in graph:
            raise ValueError(f"Invalid end hub: '{end}'")

        if ignored_hubs is None:
            ignored_hubs = set()

        if ignored_connections is None:
            ignored_connections = set()

        distances: dict[str, int | None] = {
            name: None
            for name in graph
        }

        priority_count: dict[str, int] = {
            name: -1
            for name in graph
        }

        previous: dict[str, str | None] = {
            name: None
            for name in graph
        }

        distances[start] = 0
        priority_count[start] = 0

        queue: list[tuple[int, int, str]] = []

        heapq.heappush(
            queue,
            (0, 0, start)
        )

        while queue:
            current_distance, negative_priority, current_hub = (
                heapq.heappop(queue)
            )

            current_priority: int = -negative_priority
            known_distance: int | None = distances[current_hub]

            if known_distance is None:
                continue

            if current_distance != known_distance:
                continue

            if current_priority != priority_count[current_hub]:
                continue

            if current_hub == end:
                break

            for connection in graph[current_hub]:
                opposite_hub: Hub = connection.get_opposite_hub(current_hub)

                if opposite_hub.name in ignored_hubs:
                    continue

                connection_key: frozenset[str] = frozenset(
                    {current_hub, opposite_hub.name}
                )

                if connection_key in ignored_connections:
                    continue

                zone: str = opposite_hub.properties["zone"]

                if zone == "blocked":
                    continue

                movement_cost: int = 1

                if zone == "restricted":
                    movement_cost = 2

                new_distance: int = (current_distance + movement_cost)
                new_priority: int = current_priority

                if zone == "priority":
                    new_priority += 1

                opposite_distance: int | None = (
                    distances[opposite_hub.name]
                )

                better_distance: bool = (
                    opposite_distance is None
                    or new_distance < opposite_distance
                )

                better_priority: bool = (
                    opposite_distance == new_distance
                    and new_priority
                    > priority_count[opposite_hub.name]
                )

                if better_distance or better_priority:
                    distances[opposite_hub.name] = new_distance
                    priority_count[opposite_hub.name] = new_priority
                    previous[opposite_hub.name] = current_hub

                    heapq.heappush(
                        queue,
                        (
                            new_distance,
                            -new_priority,
                            opposite_hub.name,
                        )
                    )
        return self.reconstruct_path(start, end, previous)

    def reconstruct_path(self, start: str, end: str,
                         previous: dict[str, str | None],) -> list[str]:
        """
        Reconstructs the path generated by Dijkstra.
        """
        if start == end:
            return [start]
        elif previous[end] is None:
            return []

        path: list[str] = []
        current_hub: str | None = end

        while current_hub is not None:
            path.append(current_hub)

            if current_hub == start:
                break

            current_hub = previous[current_hub]

        path.reverse()

        if not path or path[0] != start:
            return []

        return path

    def get_path_cost(self, path: list[str]) -> int:
        """
        Calculates the total movement cost of a path.
        """
        cost: int = 0

        for hub_name in path[1:]:
            hub: Hub = self.map.hubs[hub_name]

            if hub.properties["zone"] == "restricted":
                cost += 2
            else:
                cost += 1

        return cost

    def get_path_priority(self, path: list[str]) -> int:
        """
        Counts priority hubs in a path.
        """
        priority_count: int = 0

        for hub_name in path[1:]:
            hub: Hub = self.map.hubs[hub_name]

            if hub.properties["zone"] == "priority":
                priority_count += 1

        return priority_count

    def yen(self, start: str, end: str, k: int) -> list[list[str]]:
        """
        Finds up to K shortest loopless paths using Yen's algorithm.
        """
        if k <= 0:
            return []

        first_path: list[str] = self.dijkstra(self.graph, start, end)

        if not first_path:
            return []

        shortest_paths: list[list[str]] = [first_path]
        candidates: list[tuple[int, int, tuple[str, ...]]] = []
        candidate_keys: set[tuple[str, ...]] = set()

        for _ in range(1, k):
            previous_path: list[str] = shortest_paths[-1]

            for index in range(len(previous_path) - 1):
                spur_node: str = previous_path[index]
                root_path: list[str] = (previous_path[:index + 1])
                ignored_connections: set[frozenset[str]] = set()

                for path in shortest_paths:
                    if (len(path) > index and
                       path[:index + 1] == root_path):
                        connection_key: frozenset[str] = frozenset(
                            {
                                path[index],
                                path[index + 1],
                            }
                        )

                        ignored_connections.add(connection_key)

                ignored_hubs: set[str] = set(root_path[:-1])
                spur_path: list[str] = self.dijkstra(self.graph, spur_node,
                                                     end, ignored_hubs,
                                                     ignored_connections)

                if not spur_path:
                    continue

                total_path: list[str] = (root_path[:-1] + spur_path)
                path_key: tuple[str, ...] = tuple(total_path)

                if path_key in candidate_keys:
                    continue

                if total_path in shortest_paths:
                    continue

                cost: int = self.get_path_cost(total_path)
                priority: int = self.get_path_priority(total_path)

                heapq.heappush(
                    candidates,
                    (
                        cost,
                        -priority,
                        path_key,
                    )
                )
                candidate_keys.add(path_key)

            if not candidates:
                break

            _, _, selected_path = heapq.heappop(candidates)
            shortest_paths.append(list(selected_path))

        return shortest_paths

    def assign_route(self) -> list[str]:
        """
        Returns and updates the cheapest and less concurrent route
        """
        selected_route: list[str] = self.routes[0][0]
        selected_cost: int = self.routes[0][1]
        drones_in_route: int = self.routes[0][2]
        route_score: int = selected_cost + drones_in_route
        route_index: int = 0

        for count in range(1, len(self.routes)):
            score: int = self.routes[count][1] + self.routes[count][2]

            if route_score > score:
                selected_route = self.routes[count][0]
                selected_cost = self.routes[count][1]
                drones_in_route = self.routes[count][2]
                route_index = count
                route_score = score

        self.routes[route_index] = (selected_route, selected_cost,
                                    drones_in_route + 1)

        return selected_route

    def run_turn(self) -> None:
        """
        Run a turn where all drones move or wait
        """
        proposals: dict[int, str] = {}
        valid_movements: dict[int, str] = {}

        for drone in self.drones:
            next_movement: str = drone.get_next_hub_name()

            if drone.current_hub.name != next_movement:
                proposals[drone.id] = next_movement

        valid_movements = proposals.copy()
        changed: bool = True

        while changed:
            changed = False

            for hub_name, hub in self.map.hubs.items():
                if hub.is_start or hub.is_end:
                    continue

                current_drones: int = self.get_drones_in_hub(hub_name)

                leaving: int = 0
                entering: list[int] = []

                for drone_id, destination in valid_movements.items():
                    selected_drone: Drone = self.get_drone(drone_id)

                    if selected_drone.current_hub.name == hub_name:
                        leaving += 1

                    if destination == hub_name:
                        entering.append(drone_id)

                final_occupancy: int = (
                    current_drones - leaving + len(entering)
                )

                max_drones: int = hub.properties["max_drones"]

                while final_occupancy > max_drones and entering:
                    rejected_drone: int = entering.pop()

                    del valid_movements[rejected_drone]

                    final_occupancy -= 1
                    changed = True

        console: Console = Console()

        movements: list[Text] = []

        for drone_id, destination in valid_movements.items():
            actual_drone: Drone = self.get_drone(drone_id)
            next_hub: Hub = self.map.get_hub(destination)

            actual_drone.current_hub = next_hub
            actual_drone.route_index += 1

            movements.append(actual_drone.return_movement())

        if movements:
            console.print(*movements, sep=" ")

    def get_drone(self, drone_id: int) -> Drone:
        """
        Returns a Drone by its id
        """
        for drone in self.drones:
            if drone.id == drone_id:
                return drone
        raise ValueError(f"Invalid drone_id: {drone_id}")

    def get_drones_in_hub(self, hub_name: str) -> int:
        """
        Returns the amount of drones in the indicated hub
        """
        count: int = 0

        for drone in self.drones:
            if drone.current_hub.name == hub_name:
                count += 1
        return count

    def check_simulation_end(self) -> bool:
        """
        Checks if all drones have reached the meta
        """
        for drone in self.drones:
            if drone.current_hub != drone.end:
                return False
        return True
