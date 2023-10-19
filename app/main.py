import app.config as cfg
from app.flats import FlatNotifier, FlatParser, FlatScraper


def run() -> None:
    """Main function."""
    flat_scraper = FlatScraper()
    flat_scraper.url = cfg.FLAT_WEB_URL
    flat_scraper.headers = cfg.FLAT_REQUEST_HEADERS
    flat_scraper.scrap_webpage()

    if flat_scraper.error_occured:
        return 0

    flat_parser = FlatParser()
    flat_parser.load_dataframe_from_database(db_path=cfg.FLAT_DB_PATH)
    flat_parser.content_raw = flat_scraper.content
    flat_parser.classes = cfg.FLAT_WEB_CLASSES
    flat_parser.parse_raw_content_to_dataframe()

    if flat_parser.error_occured:
        return 0

    flat_notifier = FlatNotifier()
    flat_notifier.dataframe = flat_parser.content_dataframe
    flat_notifier.recipients = cfg.RECIPIENTS
    flat_notifier.sender = cfg.SENDER
    flat_notifier.send_notification()

    if flat_notifier.error_occured:
        return 0

    flat_parser.save_dataframe_in_database(db_path=cfg.FLAT_DB_PATH)

    return 1


if __name__ == "__main__":
    run()
