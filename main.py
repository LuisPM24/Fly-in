from map_parser import MapParser
from simulation import Simulation


def main() -> None:
    try:
        Simulation(MapParser())
    except Exception as e:
        print(f"Error - {e}")


if __name__ == "__main__":
    main()
