import pytest


@pytest.fixture
def author_name() -> str:
    """Test fixture"""

    return "norbert"
