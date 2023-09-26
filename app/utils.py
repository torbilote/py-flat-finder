from bs4 import BeautifulSoup as bs
import pendulum
from loguru import logger
import requests
import polars as pl
from app.config import olx_items
class Finder:
    def __init__(self, url: str) -> None:
        self._url = url
        self._response = None

    def send_http_request(self) -> None:
        response = requests.get(self._url)
        soup = bs(response.content, 'html.parser')
        data = soup.find_all('div', class_=olx_items)
        self._response = data

    def parse_content_to_dataframe(self) -> ...:
        ...

    def send_notification_to_users(self) -> ...:
        ...

    @property
    def response(self) -> str:
        return self._response
