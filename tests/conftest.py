import pytest
from typing import Any
from collections.abc import Generator
from model.destination import DestinationPostgreSQL

@pytest.fixture(scope="session")
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
