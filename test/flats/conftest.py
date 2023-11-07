import test.flats.examples as examples

import pytest

from app.flats.flat_scraper import FlatScraper


@pytest.fixture
def flat_scraper():
    flat_scraper = FlatScraper()
    flat_scraper.web_url = examples.web_url
    flat_scraper.request_headers = examples.request_headers
    return flat_scraper
