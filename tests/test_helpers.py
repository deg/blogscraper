from blogscraper.utils.helpers import greet


def test_greet() -> None:
    assert greet("Alice") == "Hello, Alice!"
    assert greet("Bob") == "Hello, Bob!"
