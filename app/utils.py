import email.utils
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TypeAlias

import bs4
import pendulum
import polars as pl
import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.config import PATH_ITEMS, WEB_CLASSES

bs_tag: TypeAlias = bs4.element.Tag | bs4.element.NavigableString | None


class Finder:
    """Finder class."""

    def __init__(self, url: str) -> None:
        """Init."""
        self._url: str = url
        self._raw_content: bs4.BeautifulSoup | None = None
        self._dataframe_current_run: pl.DataFrame | None = None

    def get_web_content(self) -> None:
        """Sends GET request to website and fetches its content."""
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
            print("Failed to fetch.", err)  # TODO LOGGER
            raise
        self._raw_content = bs4.BeautifulSoup(response.content, "html.parser")

    def parse_content_to_dataframe(self) -> None:
        """Retrieves relevant data from raw content and parses it to dataframe."""
        data: list = []
        list_of_items: list[bs4.element.Tag] = (
            self._raw_content.find_all("div", class_=WEB_CLASSES["olx_items"])
            if self._raw_content
            else []
        )
        for item in list_of_items:
            id_text: str | None = item.get("id")

            if not id_text:
                continue

            url_tag: bs_tag = item.find("a", class_=WEB_CLASSES["olx_item_url"])
            header_tag: bs_tag = item.find("h6", class_=WEB_CLASSES["olx_item_header"])
            price_tag: bs_tag = item.find("p", class_=WEB_CLASSES["olx_item_price"])
            refresh_date_tag: bs_tag = item.find(
                "p", class_=WEB_CLASSES["olx_item_refresh_date"]
            )

            url_text: str = url_tag.get("href") if url_tag else "NA"
            header_text: str = header_tag.text if header_tag else "NA"
            price_text: str = price_tag.text if header_tag else "NA"
            refresh_date_text: str = refresh_date_tag.text if refresh_date_tag else "NA"

            if url_text.startswith("/d/"):
                url_text = "https://www.olx.pl" + url_text

            data.append(
                {
                    "id": id_text,
                    "url": url_text,
                    "header": header_text,
                    "price": price_text,
                    "refresh_date": refresh_date_text,
                }
            )
        dataframe: pl.DataFrame = pl.DataFrame(data)
        dataframe_filtered: pl.DataFrame = _get_new_results_only(dataframe)
        dataframe_filtered.write_csv(file=PATH_ITEMS)
        self._dataframe_current_run = dataframe_filtered

    def send_notification_to_users(self) -> None:
        """Sends email notification to defined users."""
        email = MIMEMultipart("alternative")
        email["From"]: str = email.utils.formataddr(("NL", PRODUCER))
        email["Subject"]: str = f"{len(self._dataframe_current_run)} flat offers!"

        content: str = ""

        try:
            session = smtplib.SMTP_SSL(
                "smtp.poczta.onet.pl",
                465,
                context=ssl.create_default_context(),
                timeout=120,
            )
            session.ehlo()
            session.login(PRODUCER, PWD)

            for subscriber in SUBSCRIBERS:
                email["To"] = email.utils.formataddr(("Subscriber", subscriber))
                email.attach(MIMEText(content, "plain"))
                text = email.as_string()
                session.sendmail(BOT_EMAIL, subscriber, text)

            session.close()

        except Exception as e:
            print("Error: ", e)  # TODO LOGGER
        else:
            print(f"Mail Sent. Number of flats: {len(SUBSCRIBERS)}")  # TODO LOGGER

    @property
    def dataframe_current_run(self) -> pl.DataFrame | None:
        """Getter of attribute."""
        return self._dataframe_current_run


def _get_new_results_only(dataframe: pl.DataFrame) -> None:
    """Compares new data with existing one and appends new data only to csv file."""
    existing_df: pl.DataFrame = pl.read_csv(
        source="data/items.csv", infer_schema_length=0
    )
    existing_df_ids: pl.Series = existing_df["id"]
    new_df: pl.DataFrame = dataframe.filter(~pl.col("id").is_in(existing_df_ids))
    return pl.concat([existing_df, new_df])
