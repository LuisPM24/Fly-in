from parser import Parser


def main() -> None:
    try:
        parser = Parser()
    except Exception as e:
        print(f"Error - {e}")


if __name__ == "__main__":
    main()
