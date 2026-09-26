from map_parser import MapParser
from simulation import Simulation


def main() -> None:
    try:
        map_parser = MapParser()
        # for conn in map_parser.connections:
        #     print(f"{conn.pointA.name}-{conn.pointB.name}")
        Simulation(map_parser)
    except Exception as e:
        print(f"Error - {e}")


if __name__ == "__main__":
    main()
