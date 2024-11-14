from typing import Any
import pendulum
from datetime import datetime


class APIHelper:
    """Helper class to prepare acquisition of data from the API and handle the API data."""

    @staticmethod
    def transform(data: dict[str, Any]) -> list[tuple[str, str, float]]:
        """Filter and transform data to extract required fields.

        :param data: data acquired from the API
        :return: list of tuples containing psrType, startTime and quantity
        """
        return [('bmreports, ' + item['psrType'] + ', min30', item['startTime'], item['quantity']) for item in data['data']]

    @staticmethod
    def date_param(dt: datetime) -> pendulum.DateTime:
        """Get the start datetime for data collection.

        :param dt: datetime to be converted to nearest 30 minutes
        :return: datetime
        """
        dt = pendulum.instance(dt)

        # API published data is 90 minutes behind
        return APIHelper.floored_to_30_min(dt).subtract(minutes=90)

    @staticmethod
    def floored_to_30_min(dt: pendulum.DateTime) -> pendulum.DateTime:
        """Floor the given datetime to the nearest 30 minutes.

        :param dt: datetime to be floored
        :return: floored datetime
        """
        return dt.replace(minute=(dt.minute // 30) * 30, second=0, microsecond=0)
