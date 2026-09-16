from map_parser import MapParser


def main() -> None:
    try:
        MapParser()
    except Exception as e:
        print(f"Error - {e}")


if __name__ == "__main__":
    main()
