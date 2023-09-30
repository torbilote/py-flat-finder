from app.utils import Finder


def run() -> None:
    """Main function."""
    finder = Finder()
    finder.get_web_content()
    finder.parse_content_to_dataframe()
    finder.send_notification_to_users()


if __name__ == "__main__":
    run()
