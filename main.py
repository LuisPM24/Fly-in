from map_parser import MapParser
from simulation import Simulation


def main() -> None:
    try:
        map_parser = MapParser()
        Simulation(map_parser)
    except Exception as e:
        print(f"Error - {e}")


if __name__ == "__main__":
    main()
