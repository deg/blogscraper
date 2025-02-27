from blogscraper.utils.helpers import greet


def main() -> None:
    name = "World"
    message = greet(name)
    print(message)  # "Hello, World!"


if __name__ == "__main__":  # pragma: no cover
    main()
