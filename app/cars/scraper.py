import bs4
import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.abstracts import Scraper


class CarScraper(Scraper):
    """Car scraper class."""

    @property
    def web_url(self):
        """Gets webpage url."""
        return self._web_url

    @web_url.setter
    def web_url(self, value):
        """Sets webpage url."""
        self._web_url = value

    @property
    def request_headers(self):
        """Gets html headers."""
        return self._request_headers

    @request_headers.setter
    def request_headers(self, value):
        """Sets html headers."""
        self._request_headers = value

    @property
    def web_content(self):
        """Gets webpage content."""
        return self._web_content

    @property
    def error_occured(self):
        """Gets error_occured flag."""
        return self._error_occured

    def scrap_webpage(self):
        """Fetches webpage content."""
        with requests.Session() as session:
            retries = Retry(total=3, backoff_factor=1)
            session.mount(prefix="https://", adapter=HTTPAdapter(max_retries=retries))
            for index, car in enumerate(self._web_url):
                response = session.get(
                    url=self._web_url[car],
                    timeout=10,
                    headers=self._request_headers,
                    cookies=None,
                )
                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as error:
                    self._error_occured = True
                    logger.exception(f"{type(error).__name__}: {error}")
                else:
                    if not index:
                        self._web_content = bs4.BeautifulSoup(response.content, "lxml")
                    else:
                        self._web_content.body.append(bs4.BeautifulSoup(response.content, "lxml").body)
                    logger.info(f"Fetched web content. Page {index+1}/{len(self._web_url)}")

        return 1
