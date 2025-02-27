from pytest import CaptureFixture

from blogscraper.main import main


def test_example() -> None:
    assert 1 + 1 == 2


def test_main(capsys: CaptureFixture[str]) -> None:
    main()
    captured = capsys.readouterr()
    assert "Hello, World!" in captured.out
