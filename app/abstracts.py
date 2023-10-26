from abc import ABC, abstractmethod


class Scraper(ABC):
    """Web scraper class."""

    def __init__(self):
        """Init."""
        self._url = None
        self._classes = None
        self._content = None
        self._error_occured = False

    @property
    @abstractmethod
    def url(self):
        """Gets webpage url."""
        return self._url

    @url.setter
    @abstractmethod
    def url(self, value):
        """Sets webpage url."""
        self._url = value

    @property
    @abstractmethod
    def content(self):
        """Gets webpage content."""
        return self._content

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
        self._content_raw = None
        self._classes = None
        self._content_dataframe = None
        self._content_dataframe_in_db = None
        self._error_occured = False

    @property
    @abstractmethod
    def content_raw(self):
        """Gets raw content."""
        return self._content_raw

    @content_raw.setter
    @abstractmethod
    def content_raw(self, value):
        """Sets raw content."""
        self._content_raw = value

    @property
    @abstractmethod
    def classes(self):
        """Gets raw content."""
        return self._classes

    @classes.setter
    @abstractmethod
    def classes(self, value):
        """Sets raw content."""
        self._classes = value

    @property
    @abstractmethod
    def content_dataframe(self):
        """Gets dataframe."""
        return self._content_dataframe

    @property
    @abstractmethod
    def content_dataframe_in_db(self):
        """Gets dataframe coming from db."""
        return self._content_dataframe_in_db

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
        self._dataframe = None
        self._recipients = None
        self._sender = None
        self._error_occured = False

    @property
    @abstractmethod
    def dataframe(self):
        """Gets dataframe."""
        return self._dataframe

    @dataframe.setter
    @abstractmethod
    def dataframe(self, value):
        """Sets dataframe."""
        self._dataframe = value

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
