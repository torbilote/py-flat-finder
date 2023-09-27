import pendulum
import polars as pl
import requests
from bs4 import BeautifulSoup as bs
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.config import WEB_CLASSES


class Finder:
    """Finder class."""

    def __init__(self, url: str) -> None:
        """Init."""
        self._url: str = url
        self._raw_content: bs | None = None
        self._data_current_run: list | None = None

    @property
    def data_current_run(self) -> list | None:
        """Getter of attribute."""
        return self._data_current_run

    def get_web_content(self) -> None:
        """Send GET request to website and fetch its content."""
        session: requests.Session = requests.Session()
        retries: Retry = Retry(total=3, backoff_factor=1)
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response: requests.Response = session.get(
            url=self._url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
            },
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            raise
        self._raw_content = bs(response.content, "html.parser")

    def parse_content_to_dataframe(self) -> None:
        """Retrieve relevant data from raw content and parse it to dataframe."""
        data: list = []
        items: list = (
            self._raw_content.find_all("div", class_=WEB_CLASSES["olx_items"])
        )
        for item in items:
            id_text: str | None = item.get("id")
            if not id_text:
                continue

            url_tag = item.find("a", class_=WEB_CLASSES["olx_item_url"])
            header_tag = item.find("h6", class_=WEB_CLASSES["olx_item_header"])
            price_tag = item.find("p", class_=WEB_CLASSES["olx_item_price"])
            refresh_dt_tag = item.find("p", class_=WEB_CLASSES["olx_item_refresh_dt"])

            url_text: str = url_tag["href"] if url_tag else "NA"
            header_text: str = header_tag.text if header_tag else "NA"
            price_text: str = price_tag.text if header_tag else "NA"
            refresh_dt_text: str = refresh_dt_tag.text if refresh_dt_tag else "NA"

            if url_text.startswith("/d/"):
                url_text = "https://www.olx.pl" + url_text

            data.append(
                {
                    "id": id_text,
                    "url": url_text,
                    "header": header_text,
                    "price": price_text,
                    "refresh_date": refresh_dt_text,
                }
            )
        self._data_current_run = data

    def send_notification_to_users(self) -> None:
        """Send email notification to defined users."""
