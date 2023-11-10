import app.config as main_cfg
import app.flats.config as cfg
from app.abstracts import Runner
from app.flats.notifier import FlatNotifier
from app.flats.parser import FlatParser
from app.flats.scraper import FlatScraper


class FlatRunner(Runner):
    """Flat notifier class."""

    def run(self):
        """Execute runner's logic."""
        flat_scraper = FlatScraper()
        flat_scraper.web_url = cfg.WEB_URL
        flat_scraper.request_headers = cfg.REQUEST_HEADERS
        flat_scraper.scrap_webpage()

        if flat_scraper.error_occured:
            return 0

        flat_parser = FlatParser()
        flat_parser.load_dataframe_from_database(cfg.FILE_PATH_LOCAL, cfg.FILE_ID_DB)
        flat_parser.raw_content = flat_scraper.web_content
        flat_parser.web_classes = cfg.WEB_CLASSES
        flat_parser.parse_raw_content_to_dataframe()

        if flat_parser.error_occured:
            return 0

        flat_notifier = FlatNotifier()
        flat_notifier.data = flat_parser.dataframe
        flat_notifier.recipients = cfg.RECIPIENTS
        flat_notifier.sender = main_cfg.SENDER
        flat_notifier.send_notification()

        if flat_notifier.error_occured:
            return 0

        flat_parser.save_dataframe_in_database(cfg.FILE_PATH_LOCAL, cfg.FILE_ID_DB)
        return 1
