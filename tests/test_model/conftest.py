import pytest
from typing import Any
from model.source import SourceAPI

@pytest.fixture
def _mock_requests_get(monkeypatch: Any, mock_data: dict[str, list[dict[str, Any]]]) -> None:
    """Monkeypatch the requests.get() method to return a mock response.

    :param monkeypatch: The pytest monkeypatch fixture.
    :param mock_data: The mock data fixture.
    :return: None.
    """
    def mock_get(url: str) -> Any:
        class MockResponse:
            status_code = 200
            def json(self) -> dict[str, list[dict[str, Any]]]:
                return mock_data

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_get)

@pytest.fixture
def api_mocker(_mock_requests_get: Any) -> SourceAPI:
    """Instantiate the SourceAPI with monkey patch.

    :param _mock_requests_get: The mock_requests_get fixture.
    :return: SourceAPI instance.
    """
    return SourceAPI()
