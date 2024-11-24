from typing import Any
from datetime import datetime, timezone
import pendulum
from helper.api_helper import APIHelper


class TestAPIHelper:
    """"Test class for APIHelper."""

    def test_transform(self, mock_data: dict[str, list[dict[str, Any]]]) -> None:
        """Test the transform method.

        :param mock_data: Mock data from fixture.
        """
        assert APIHelper.transform(mock_data) == [
            ('bmreports, Wind Onshore, min30', '2023-07-21T04:30:00Z', 640.283),
            ('bmreports, Wind Offshore, min30', '2023-07-21T04:30:00Z', 77.014),
            ('bmreports, Solar, min30', '2023-07-21T04:30:00Z', 89.0),
        ]

    def test_date_param(self) -> None:
        """Test the date_param method."""
        assert APIHelper.date_param(
            pendulum.instance(datetime(2024, 10, 16, 10, 45, tzinfo=timezone.utc))) == pendulum.instance(
            datetime(2024, 10, 16, 9, 0, tzinfo=timezone.utc))

    def test_floored_to_30_min(self) -> None:
        """"Test the floored_to_30_min method."""
        assert APIHelper.floored_to_30_min(
            pendulum.instance(datetime(2024, 10, 16, 10, 45, tzinfo=timezone.utc))) == pendulum.instance(
            datetime(2024, 10, 16, 10, 30, tzinfo=timezone.utc))
