import pendulum
from model.source import SourceAPI


class TestSourceAPI:
    """Test class for SourceAPI."""

    def test_url_friendly_datetime(self, api_mocker: SourceAPI) -> None:
        """Test that datetime is correctly formatted for the API URL.

        :param api_mocker: Mocked SourceAPI object from fixture.
        """
        assert api_mocker.url_friendly_datetime(pendulum.datetime(2024, 10, 16, 14, 30)) == "2024-10-16%2014%3A30"

    def test_fetch_json(self, api_mocker: SourceAPI) -> None:
        """Test the API data fetching functionality with mocked response.

        :param api_mocker: Mocked SourceAPI object from fixture.
        """
        from_date = pendulum.datetime(2024, 10, 10)
        to_date = pendulum.datetime(2024, 10, 12)

        # Call the method that fetches the JSON
        result = api_mocker.fetch_json(from_date, to_date)

        assert isinstance(result, dict)
        assert result["data"][0]["psrType"] == "Wind Onshore"
        assert result["data"][1]["psrType"] == "Wind Offshore"
