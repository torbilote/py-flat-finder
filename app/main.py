from app.config import WEB_URL
from app.utils import Finder


def run() -> None:
    """Main function."""
    finder = Finder(WEB_URL)
    finder.get_web_content()
    finder.parse_content_to_dataframe()
    print(finder.data_current_run)

if __name__ == "__main__":
    run()
