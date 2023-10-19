import email.utils
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bs4
import pendulum
import polars as pl
import requests
from loguru import logger
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from app.classes.abstracts import Notifier, Parser, Scraper


class FlatScraper(Scraper):
    """Flat scraper class."""

    @property
    def url(self):
        """Gets webpage url."""
        return self._url

    @url.setter
    def url(self, value):
        """Sets webpage url."""
        self._url = value

    @property
    def headers(self):
        """Gets html headers."""
        return self._headers

    @headers.setter
    def headers(self, value):
        """Sets html headers."""
        self._headers = value

    @property
    def content(self):
        """Gets webpage content."""
        return self._content

    @property
    def error_occured(self):
        """Gets error_occured flag."""
        return self._error_occured

    def scrap_webpage(self):
        """Fetches webpage content."""
        with requests.Session() as session:
            retries = Retry(total=3, backoff_factor=1)
            session.mount(prefix="https://", adapter=HTTPAdapter(max_retries=retries))
            response = session.get(url=self._url, timeout=10, headers=self._headers)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as error:
                self._error_occured = True
                logger.exception(f"{type(error).__name__}: {error}")
            else:
                self._content = bs4.BeautifulSoup(response.content, "html.parser")
                logger.info("Fetched web content.")


class FlatParser(Parser):
    """Flat parser class."""

    @property
    def content_raw(self):
        """Gets raw content."""
        return self._content_raw

    @content_raw.setter
    def content_raw(self, value):
        """Sets raw content."""
        self._content_raw = value

    @property
    def classes(self):
        """Gets raw content."""
        return self._classes

    @classes.setter
    def classes(self, value):
        """Sets raw content."""
        self._classes = value

    @property
    def content_dataframe(self):
        """Gets dataframe."""
        return self._content_dataframe

    @property
    def content_dataframe_in_db(self):
        """Gets dataframe from db."""
        return self._content_dataframe_in_db

    @property
    def error_occured(self):
        """Gets error_occured flag."""
        return self._error_occured

    def parse_raw_content_to_dataframe(self):
        """Parses raw webpage content to dataframe."""
        schema = [
            ("id", pl.Utf8),
            ("url", pl.Utf8),
            ("header", pl.Utf8),
            ("price", pl.Utf8),
            ("refresh_date", pl.Utf8),
            ("created_timestamp", pl.Utf8),
        ]
        dataframe = pl.DataFrame(schema=schema)
        items = self._content_raw.find_all("div", class_=self._classes["olx_items"])
        for item in items:
            id_text = item.get("id", "")

            if not id_text:
                continue

            url_tag = item.find("a", class_=self._classes["olx_item_url"])
            header_tag = item.find("h6", class_=self._classes["olx_item_header"])
            price_tag = item.find("p", class_=self._classes["olx_item_price"])
            refresh_dt_tag = item.find("p", class_=self._classes["olx_item_refresh_dt"])

            url_text = url_tag.get("href") if url_tag else "NA"
            header_text = header_tag.text if header_tag else "NA"
            price_text = price_tag.text if price_tag else "NA"
            refresh_dt_text = refresh_dt_tag.text if refresh_dt_tag else "NA"

            if url_text.startswith("/d/"):
                url_text = "https://www.olx.pl" + url_text

            item_data = {
                "id": id_text,
                "url": url_text,
                "header": header_text,
                "price": price_text,
                "refresh_date": refresh_dt_text,
                "created_timestamp": pendulum.now().format("YYYY-MM-DD HH:mm:ss"),
            }

            dataframe.vstack(pl.DataFrame(item_data), in_place=True)

        dataframe_from_db_ids = self._content_dataframe_in_db["id"]

        self._content_dataframe = dataframe.filter(
            ~pl.col("id").is_in(dataframe_from_db_ids)
        )
        logger.info("Parsed raw content to dataframe.")

    def load_dataframe_from_database(self, db_path):
        self._content_dataframe_in_db = pl.read_csv(
            source=db_path, infer_schema_length=0
        )
        logger.info("Loaded dataframe from database.")

    def save_dataframe_in_database(self, db_path):
        dataframe = pl.concat([self._content_dataframe_in_db, self._content_dataframe])
        dataframe.write_csv(file=db_path)
        logger.info("Saved dataframe in database.")


class FlatNotifier(Notifier):
    """Flat notifier class."""

    def __init__(self):
        """Init."""
        super().__init__()
        self._email_body = None

    @property
    def dataframe(self):
        """Gets dataframe."""
        return self._dataframe

    @dataframe.setter
    def dataframe(self, value):
        """Sets dataframe."""
        self._dataframe = value

    @property
    def recipients(self):
        """Gets notification recipients."""
        return self._recipients

    @recipients.setter
    def recipients(self, value):
        """Sets notification recipients."""
        self._recipients = value

    @property
    def sender(self):
        """Gets sender credentials."""
        return self._sender

    @sender.setter
    def sender(self, value):
        """Sets sender credentials."""
        self._sender = value

    @property
    def error_occured(self):
        """Gets error_occured flag."""
        return self._error_occured

    def send_notification(self):
        """Sends email notification to recipients."""
        smtp_session_config = {
            "host": "smtp.poczta.onet.pl",
            "port": 465,
            "context": ssl.create_default_context(),
            "timeout": 120,
        }
        smtp_exceptions = (
            smtplib.SMTPConnectError,
            smtplib.SMTPAuthenticationError,
            smtplib.SMTPHeloError,
            smtplib.SMTPNotSupportedError,
            smtplib.SMTPRecipientsRefused,
            smtplib.SMTPSenderRefused,
            smtplib.SMTPDataError,
        )
        self._prepare_email()
        try:
            with smtplib.SMTP_SSL(**smtp_session_config) as session:
                session.ehlo()
                session.login(
                    user=self._sender["email"], password=self._sender["password"]
                )
                fails = session.sendmail(
                    from_addr=self._sender["email"],
                    to_addrs=self._recipients,
                    msg=self._email_body,
                )
                if fails:
                    raise smtplib.SMTPNotSupportedError(f"Errors: {fails}")
        except smtp_exceptions as error:
            logger.exception(f"{type(error).__name__}: {error}")
            self._error_occured = True
        else:
            logger.info("Sent notification to recipients.")

    def _prepare_email(self):
        """Prepares email content to recipients."""
        email_text_message_array = [
            f'{item["url"]} - {item["header"]} - {item["price"]} - {item["refresh_date"]}'
            for item in self._dataframe.iter_rows(named=True)
        ]
        email_text_message = "\n".join(email_text_message_array)
        email_config = MIMEMultipart("alternative")
        email_config["From"] = email.utils.formataddr(("NL", self._sender["email"]))
        email_config["Subject"] = f"{len(self._dataframe)} flat offers!"
        email_config["To"] = email.utils.formataddr((None, "Subscriber"))
        email_config.attach(MIMEText(email_text_message, "plain"))
        self._email_body = email_config.as_string()
