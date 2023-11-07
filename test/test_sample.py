import pytest


@pytest.mark.parametrize("number", [1, 2, 3, 4])
def test_foo(author_name: str, number: int) -> None:
    """Testing function"""

    assert author_name == "norbert"
    assert number in range(5)
