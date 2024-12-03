import email.utils
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from app.abstracts import Notifier


class CarNotifier(Notifier):
    """Car notifier class."""

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
        email_config["Subject"] = f"{len(self._data)} car offers!"
        email_config["To"] = email.utils.formataddr((None, "Subscriber"))
        email_config.attach(MIMEText(email_text_message, "plain"))
        self._email_body = email_config.as_string()
        return 1
