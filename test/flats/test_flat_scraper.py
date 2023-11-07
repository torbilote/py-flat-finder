import test.flats.examples as examples


def test_property_web_url(flat_scraper):
    assert flat_scraper.web_url == examples.web_url


def test_property_request_headers(flat_scraper):
    assert flat_scraper.request_headers == examples.request_headers
