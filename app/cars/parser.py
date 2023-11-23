import io

import pendulum
import polars as pl
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from loguru import logger

from app.abstracts import Parser


class CarParser(Parser):
    """Car parser class."""

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

        available_offers_count_tag = self._raw_content.find("span", class_=self._web_classes["olx_number_of_offers"])
        available_offers_count_text = available_offers_count_tag.find("span").text
        print(available_offers_count_text)

        if " 0 " in available_offers_count_text:
            logger.warning("Cancelled as no data available.")
            return 0

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

    def load_dataframe_from_database(self, db_path, file_id):
        scope = ["https://www.googleapis.com/auth/drive"]
        service_account_json_key = "app/sa-google-drive-credentials.json"
        credentials = service_account.Credentials.from_service_account_file(
            filename=service_account_json_key, scopes=scope
        )
        service = build("drive", "v3", credentials=credentials)
        file_on_disk = service.files().get_media(fileId=file_id)
        stream_io = io.BytesIO()
        MediaIoBaseDownload(stream_io, file_on_disk).next_chunk()
        file_downloaded = stream_io.getvalue()
        with open(db_path, "wb") as f:
            f.write(file_downloaded)

        self._data_from_db = pl.read_csv(source=db_path, infer_schema_length=0)
        logger.info(
            f"Loaded dataframe from database. Number of rows: {len(self._data_from_db)}."
        )
        return 1

    def save_dataframe_in_database(self, db_path, file_id):
        dataframe = pl.concat([self._data_from_db, self._dataframe])
        dataframe.write_csv(file=db_path)

        scope = ["https://www.googleapis.com/auth/drive"]
        service_account_json_key = "app/sa-google-drive-credentials.json"
        credentials = service_account.Credentials.from_service_account_file(
            filename=service_account_json_key, scopes=scope
        )
        service = build("drive", "v3", credentials=credentials)
        media = MediaFileUpload(db_path, mimetype="text/csv")
        _file = service.files().update(fileId=file_id, media_body=media).execute()
        logger.info(
            f"Saved dataframe in database. Number of new rows: {len(self._dataframe)}."
        )
        return 1
