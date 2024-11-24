import pytest
from typing import Any
from airflow.models import DagBag

@pytest.fixture(scope='module')
def dag_psr_sync() -> DagBag | Any:
    """Initialize the power_data_sync_dag."""
    bag = DagBag().get_dag("psr_sync")
    bag.id = "psr_sync"

    return bag
