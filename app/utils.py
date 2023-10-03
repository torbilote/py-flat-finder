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

from app.config import (
    PATH_ITEMS,
    REQUEST_HEADERS,
    SENDER_EMAIL,
    SENDER_PWD,
    SUBSCRIBERS,
    WEB_CLASSES,
    WEB_URL,
)


class Finder:
    """Finder class."""

    bs_tag: TypeAlias = bs4.element.Tag | bs4.element.NavigableString | str
    smtp_errors: TypeAlias = tuple[type[smtplib.SMTPException], ...]

    def __init__(self) -> None:
        """Init."""
        self._url: str
        self._classes: dict[str, str]
        self._raw_content: bs4.BeautifulSoup
        self._dataframe_current_run: pl.DataFrame

        self._url = WEB_URL
        self._classes = WEB_CLASSES
        self._raw_content = bs4.BeautifulSoup()
        self._dataframe_current_run = pl.DataFrame()

    def get_web_content(self) -> None:
        """Sends GET request to website and fetches its content."""
        session: requests.Session
        retries: Retry
        response: requests.Response

        session = requests.Session()
        retries = Retry(total=3, backoff_factor=1)
        session.mount(prefix="https://", adapter=HTTPAdapter(max_retries=retries))
        response = session.get(url=self._url, timeout=10, headers=REQUEST_HEADERS)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Failed to fetch.", err)  # TODO LOGGER
            raise

        self._raw_content = bs4.BeautifulSoup(response.content, "html.parser")

    def parse_content_to_dataframe(self) -> None:
        """Retrieves relevant data from raw content and parses it to dataframe."""
        items: list[bs4.element.Tag]
        id_text: str
        url_tag: Finder.bs_tag
        header_tag: Finder.bs_tag
        price_tag: Finder.bs_tag
        refresh_dt_tag: Finder.bs_tag
        url_text: str
        header_text: str
        price_text: str
        refresh_dt_text: str
        dataframe: pl.DataFrame
        dataframe_new_only: pl.DataFrame
        dataframe_combined: pl.DataFrame

        dataframe = pl.DataFrame()
        items = self._raw_content.find_all("div", class_=self._classes["olx_items"])

        for item in items:
            id_text = item.get("id", "")

            if not id_text:
                continue

            url_tag = item.find("a", class_=WEB_CLASSES["olx_item_url"])
            header_tag = item.find("h6", class_=WEB_CLASSES["olx_item_header"])
            price_tag = item.find("p", class_=WEB_CLASSES["olx_item_price"])
            refresh_dt_tag = item.find("p", class_=WEB_CLASSES["olx_item_refresh_dt"])

            url_text = url_tag.get("href") if url_tag else "NA"
            header_text = header_tag.text if header_tag else "NA"
            price_text = price_tag.text if price_tag else "NA"
            refresh_dt_text = refresh_dt_tag.text if refresh_dt_tag else "NA"

            if url_text.startswith("/d/"):
                url_text = "https://www.olx.pl" + url_text

            dataframe.vstack(
                pl.DataFrame(
                    {
                        "id": id_text,
                        "url": url_text,
                        "header": header_text,
                        "price": price_text,
                        "refresh_date": refresh_dt_text,
                        "created_timestamp": pendulum.now().format(
                            "YYYY-MM-DD HH:mm:ss"
                        ),
                    }
                ),
                in_place=True,
            )

        dataframe_new_only, dataframe_combined = _get_filtered_results(dataframe)
        self._dataframe_current_run = dataframe_new_only
        dataframe_combined.write_csv(file=PATH_ITEMS)

    def send_notification_to_users(self) -> None:
        """Sends email notification to defined users."""
        email_body: MIMEMultipart
        email_body_as_string: str
        email_message: str
        session: smtplib.SMTP_SSL
        smtp_exceptions: Finder.smtp_errors

        email_message = "\n".join(
            [
                f'{item["url"]} - {item["header"]} - {item["price"]} - {item["refresh_date"]}'
                for item in self._dataframe_current_run.iter_rows(named=True)
            ]
        )

        email_body = MIMEMultipart("alternative")
        email_body["From"] = email.utils.formataddr(("NL", SENDER_EMAIL))
        email_body["Subject"] = f"{len(self._dataframe_current_run)} flat offers!"
        email_body["To"] = email.utils.formataddr((None, "Subscriber"))
        email_body.attach(MIMEText(email_message, "plain"))
        email_body_as_string = email_body.as_string()

        smtp_exceptions = (
            smtplib.SMTPConnectError,
            smtplib.SMTPAuthenticationError,
            smtplib.SMTPHeloError,
            smtplib.SMTPNotSupportedError,
        )
        try:
            session = smtplib.SMTP_SSL(
                "smtp.poczta.onet.pl",
                465,
                context=ssl.create_default_context(),
                timeout=120,
            )
            session.ehlo()
            session.login(user=SENDER_EMAIL, password=SENDER_PWD)
            session.sendmail(
                from_addr=SENDER_EMAIL, to_addrs=SUBSCRIBERS, msg=email_body_as_string
            )
            session.close()

        except smtp_exceptions as err:
            print("Error: ", type(err), err)  # TODO LOGGER
        else:
            print(
                f"Mail Sent. Number of flats: {len(self._dataframe_current_run)}. Number of subscribers: {len(SUBSCRIBERS)}"
            )  # TODO LOGGER


def _get_filtered_results(dataframe: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Compares new data with existing one and appends new data only to csv file."""
    existing_df: pl.DataFrame
    existing_df_ids: pl.Series
    new_df: pl.DataFrame

    existing_df = pl.read_csv(source=PATH_ITEMS, infer_schema_length=0)
    existing_df_ids = existing_df["id"]
    new_df = dataframe.filter(~pl.col("id").is_in(existing_df_ids))
    return new_df, pl.concat([existing_df, new_df])
