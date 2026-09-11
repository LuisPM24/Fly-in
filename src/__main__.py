from .classes import Parser


def main() -> None:
    parser = Parser().get_args()
    print(parser.get_map())
    print(parser.get_representation())


if __name__ == "__main__":
    main()
