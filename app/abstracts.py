from abc import ABC, abstractmethod


class Scraper(ABC):
    """Web scraper class."""

    def __init__(self):
        """Init."""
        self._web_url = None
        self._request_headers = None
        self._web_content = None
        self._error_occured = False

    @property
    @abstractmethod
    def web_url(self):
        """Gets webpage url."""
        return self._web_url

    @web_url.setter
    @abstractmethod
    def web_url(self, value):
        """Sets webpage url."""
        self._web_url = value

    @property
    @abstractmethod
    def request_headers(self):
        """Gets html headers."""
        return self._request_headers

    @request_headers.setter
    def request_headers(self, value):
        """Sets html headers."""
        self._request_headers = value

    @property
    @abstractmethod
    def web_content(self):
        """Gets webpage content."""
        return self._web_content

    @property
    @abstractmethod
    def error_occured(self):
        """Gets error_occured flag."""
        return self._error_occured

    @abstractmethod
    def scrap_webpage(self):
        """Fetches webpage content."""


class Parser(ABC):
    """Parser class."""

    def __init__(self):
        """Init."""
        self._raw_content = None
        self._web_classes = None
        self._dataframe = None
        self._data_from_db = None
        self._error_occured = False

    @property
    @abstractmethod
    def raw_content(self):
        """Gets raw content."""
        return self._raw_content

    @raw_content.setter
    @abstractmethod
    def raw_content(self, value):
        """Sets raw content."""
        self._raw_content = value

    @property
    @abstractmethod
    def web_classes(self):
        """Gets raw content."""
        return self._web_classes

    @web_classes.setter
    @abstractmethod
    def web_classes(self, value):
        """Sets raw content."""
        self._web_classes = value

    @property
    @abstractmethod
    def dataframe(self):
        """Gets dataframe."""
        return self._dataframe

    @property
    @abstractmethod
    def data_from_db(self):
        """Gets dataframe coming from db."""
        return self._data_from_db

    @property
    @abstractmethod
    def error_occured(self):
        """Gets error_occured flag."""
        return self._error_occured

    @abstractmethod
    def parse_raw_content_to_dataframe(self):
        """Parses raw webpage content to dataframe."""

    @abstractmethod
    def load_dataframe_from_database(self, db_path):
        """Loads dataframe from database."""

    @abstractmethod
    def save_dataframe_in_database(self, db_path):
        """Saves dataframe in database."""


class Notifier(ABC):
    """Notifier class."""

    def __init__(self):
        """Init."""
        self._data = None
        self._recipients = None
        self._sender = None
        self._error_occured = False

    @property
    @abstractmethod
    def data(self):
        """Gets dataframe."""
        return self._data

    @data.setter
    @abstractmethod
    def data(self, value):
        """Sets dataframe."""
        self._data = value

    @property
    @abstractmethod
    def recipients(self):
        """Gets notification recipients."""
        return self._recipients

    @recipients.setter
    @abstractmethod
    def recipients(self, value):
        """Sets notification recipients."""
        self._recipients = value

    @property
    @abstractmethod
    def sender(self):
        """Gets sender credentials."""
        return self._sender

    @sender.setter
    @abstractmethod
    def sender(self, value):
        """Sets sender credentials."""
        self._sender = value

    @property
    @abstractmethod
    def error_occured(self):
        """Gets error_occured flag."""
        return self._error_occured

    @abstractmethod
    def send_notification(self):
        """Sends notification to recipients."""


class Runner(ABC):
    """Runner class."""

    def __init__(self):
        """Init."""
        self.is_finished = False
        self.error_occured = False

    @abstractmethod
    def run(self):
        """Execute runner's logic."""
