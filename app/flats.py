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

import app.config as cfg
from app.abstracts import Notifier, Parser, Runner, Scraper


class FlatScraper(Scraper):
    """Flat scraper class."""

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
            response = session.get(
                url=self._web_url,
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
                # self._content = bs4.BeautifulSoup(response.content, "html.parser")
                self._web_content = bs4.BeautifulSoup(response.content, "lxml")
                logger.info("Fetched web content.")
        return 1


class FlatParser(Parser):
    """Flat parser class."""

    @property
    def raw_content(self):
        """Gets raw content."""
        return self._raw_content

    @raw_content.setter
    def raw_content(self, value):
        """Sets raw content."""
        self._raw_content = value

    @property
    def web_classes(self):
        """Gets raw content."""
        return self._web_classes

    @web_classes.setter
    def web_classes(self, value):
        """Sets raw content."""
        self._web_classes = value

    @property
    def dataframe(self):
        """Gets dataframe."""
        return self._dataframe

    @property
    def data_from_db(self):
        """Gets dataframe from db."""
        return self._data_from_db

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
        df = pl.DataFrame(schema=schema)
        items = self._raw_content.find_all("div", class_=self._web_classes["olx_items"])
        for item in items:
            id_text = item.get("id", "")

            if not id_text:
                continue

            url_tag = item.find("a", class_=self._web_classes["olx_item_url"])
            header_tag = item.find("h6", class_=self._web_classes["olx_item_header"])
            price_tag = item.find("p", class_=self._web_classes["olx_item_price"])
            refresh_dt_tag = item.find(
                "p", class_=self._web_classes["olx_item_refresh_dt"]
            )

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

            df.vstack(pl.DataFrame(item_data), in_place=True)

        ids = self._data_from_db["id"]
        self._dataframe = df.filter(~pl.col("id").is_in(ids))
        logger.info(
            f"Parsed raw content to dataframe. Number of new rows: {len(self._dataframe)}."
        )
        return 1

    def load_dataframe_from_database(self, db_path):
        self._data_from_db = pl.read_csv(source=db_path, infer_schema_length=0)
        logger.info(
            f"Loaded dataframe from database. Number of rows: {len(self._data_from_db)}."
        )
        return 1

    def save_dataframe_in_database(self, db_path):
        dataframe = pl.concat([self._data_from_db, self._dataframe])
        dataframe.write_csv(file=db_path)
        logger.info(
            f"Saved dataframe in database. Number of new rows: {len(self._dataframe)}."
        )
        return 1


class FlatNotifier(Notifier):
    """Flat notifier class."""

    def __init__(self):
        """Init."""
        super().__init__()
        self._email_body = None

    @property
    def data(self):
        """Gets dataframe."""
        return self._data

    @data.setter
    def data(self, value):
        """Sets dataframe."""
        self._data = value

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
        if self._data.is_empty():
            logger.warning("Cancelled as no data available.")
            self._error_occured = True
            return 0

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
            logger.info(
                f"Sent notification to recipients. Number of rows: {len(self._data)}."
            )
        return 1

    def _prepare_email(self):
        """Prepares email content to recipients."""
        email_text_message_array = [
            f'{item["url"]} - {item["header"]} - {item["price"]} - {item["refresh_date"]}'
            for item in self._data.iter_rows(named=True)
        ]
        email_text_message = "\n".join(email_text_message_array)
        email_config = MIMEMultipart("alternative")
        email_config["From"] = email.utils.formataddr(("NL", self._sender["email"]))
        email_config["Subject"] = f"{len(self._data)} flat offers!"
        email_config["To"] = email.utils.formataddr((None, "Subscriber"))
        email_config.attach(MIMEText(email_text_message, "plain"))
        self._email_body = email_config.as_string()
        return 1


class FlatRunner(Runner):
    """Flat notifier class."""

    def run(self):
        """Execute runner's logic."""
        flat_scraper = FlatScraper()
        flat_scraper.web_url = cfg.FLAT_WEB_URL
        flat_scraper.request_headers = cfg.FLAT_REQUEST_HEADERS
        flat_scraper.scrap_webpage()

        if flat_scraper.error_occured:
            return 0

        flat_parser = FlatParser()
        flat_parser.load_dataframe_from_database(db_path=cfg.FLAT_DB_PATH)
        flat_parser.raw_content = flat_scraper.web_content
        flat_parser.web_classes = cfg.FLAT_WEB_CLASSES
        flat_parser.parse_raw_content_to_dataframe()

        if flat_parser.error_occured:
            return 0

        flat_notifier = FlatNotifier()
        flat_notifier.data = flat_parser.dataframe
        flat_notifier.recipients = cfg.RECIPIENTS
        flat_notifier.sender = cfg.SENDER
        flat_notifier.send_notification()

        if flat_notifier.error_occured:
            return 0

        flat_parser.save_dataframe_in_database(db_path=cfg.FLAT_DB_PATH)
        return 1
