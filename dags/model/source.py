import pendulum
import requests
from typing import Any, cast
from urllib.parse import quote


class SourceAPI:
    """The class is intended to read  the data from API for shipping to warehouse destination."""

    API_URL = ('https://data.elexon.co.uk/bmrs/api/v1/generation/actual/per-type/'
               'wind-and-solar?from={from_date}&to={to_date}&format=json')
    STATUS_OK = 200  # HTTP status code for successful request

    def __init__(self) -> None:
        """Initialize class."""
        pass

    def url_friendly_datetime(self, dt: pendulum.DateTime) -> str:
        """To format datetime object for API query.

        :param dt: datetime object
        :return:
        """
        return quote(dt.strftime('%Y-%m-%d %H:%M'))

    def fetch_json(self, from_date: pendulum.DateTime, to_date: pendulum.DateTime) -> dict[str, Any]:
        """Fetch JSON data from API.

        :param from_date:   from start date in datetime format
        :param to_date:     to start date in datetime format
        :return:            JSON data as a dictionary
        """
        url = SourceAPI.API_URL.format(from_date=self.url_friendly_datetime(from_date),
                             to_date=self.url_friendly_datetime(to_date))

        response = requests.get(url)

        if response.status_code != self.STATUS_OK:
            raise Exception(f"Failed to fetch data: {response.status_code}")

        return cast(dict[str, Any], response.json())
