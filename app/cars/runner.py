import app.cars.config as cfg
import app.config as main_cfg
from app.abstracts import Runner
from app.cars.notifier import CarNotifier
from app.cars.parser import CarParser
from app.cars.scraper import CarScraper


class CarRunner(Runner):
    """Car notifier class."""

    def run(self):
        """Execute runner's logic."""
        car_scraper = CarScraper()
        car_scraper.web_url = cfg.WEB_URLS
        car_scraper.request_headers = cfg.REQUEST_HEADERS
        car_scraper.scrap_webpage()

        if car_scraper.error_occured:
            return 0

        car_parser = CarParser()
        car_parser.load_dataframe_from_database(cfg.FILE_PATH_LOCAL, cfg.FILE_ID_DB)
        car_parser.raw_content = car_scraper.web_content
        car_parser.web_classes = cfg.WEB_CLASSES
        car_parser.parse_raw_content_to_dataframe()

        if car_parser.error_occured:
            return 0

        car_notifier = CarNotifier()
        car_notifier.data = car_parser.dataframe
        car_notifier.recipients = cfg.RECIPIENTS
        car_notifier.sender = main_cfg.SENDER
        car_notifier.send_notification()

        if car_notifier.error_occured:
            return 0

        car_parser.save_dataframe_in_database(cfg.FILE_PATH_LOCAL, cfg.FILE_ID_DB)
        return 1
