import pytest
from typing import Any
from collections.abc import Generator
from airflow.models import DagBag
from validation.parameter_validation import ParameterValidator
from model.source import SourceAPI
from model.destination import DestinationPostgreSQL


@pytest.fixture(scope='class')
def dag_psr_sync() -> DagBag | Any:
    """Initialize the power_data_sync_dag."""
    bag = DagBag().get_dag("psr_sync")
    bag.id = "psr_sync"

    return bag

@pytest.fixture(scope='class')
def parameter_validator() -> ParameterValidator:
    """Initialize the ParameterValidator."""
    return ParameterValidator("2024-10-15 00:00", "2024-10-16 00:30")

@pytest.fixture(scope='class')
def parameter_validator_with_invalid_dates() -> ParameterValidator:
    """Initialize the ParameterValidator."""
    return ParameterValidator("invalid", "2024-10-16 00:30")

@pytest.fixture(autouse=True)
def mock_data() -> dict[str, list[dict[str, Any]]]:
    """Fixture to provide mock data for testing."""
    return {
        'data': [
            {
                "publishTime": "2023-07-21T06:58:08Z",
                "businessType": "Wind generation",
                "psrType": "Wind Onshore",
                "quantity": 640.283,
                "startTime": "2023-07-21T04:30:00Z",
                "settlementDate": "2023-07-21",
                "settlementPeriod": 12,
            },
            {
                "publishTime": "2023-07-21T06:58:08Z",
                "businessType": "Wind generation",
                "psrType": "Wind Offshore",
                "quantity": 77.014,
                "startTime": "2023-07-21T04:30:00Z",
                "settlementDate": "2023-07-21",
                "settlementPeriod": 12,
            },
            {
                "publishTime": "2023-07-21T06:58:08Z",
                "businessType": "Solar generation",
                "psrType": "Solar",
                "quantity": 89,
                "startTime": "2023-07-21T04:30:00Z",
                "settlementDate": "2023-07-21",
                "settlementPeriod": 12,
            },
        ],
    }

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

@pytest.fixture(scope="session")
def destination() -> Generator[DestinationPostgreSQL, None, None]:
    """Fixture to instantiate the DestinationPostgreSQL class."""
    dest = DestinationPostgreSQL()

    # Perform setup actions if needed (e.g., create table)
    dest.TABLE_NAME = "test_psr"

    dest.query(f"""
    DROP TABLE IF EXISTS {dest.TABLE_NAME};
    CREATE TABLE {dest.TABLE_NAME} (
        curve_name VARCHAR(255),
        curve_date TIMESTAMP NOT NULL,
        value NUMERIC,
        PRIMARY KEY (curve_name, curve_date)
    );""")

    # Yield instance for use in tests
    yield dest

    # Drop the table after the session ends
    dest.query(f"DROP TABLE IF EXISTS {dest.TABLE_NAME};")
    dest.disconnect()
