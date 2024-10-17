import logging
import pendulum
from typing import Any, cast

from model.destination import DestinationPostgreSQL as Destination
from model.source import SourceAPI as Source
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.models import DagRun
from helper.api_helper import APIHelper as Helper
from validation.parameter_validation import ParameterValidator as Validator

# Use the Airflow task logger
logger = logging.getLogger("airflow.task")

# Default date to identify the logical DAG run
DEFAULT_DATE = pendulum.now(tz="UTC").format('YYYY-MM-DD HH:mm')

@dag(
    schedule='*/30 * * * *', # Run every 30 minutes
    start_date=pendulum.datetime(2024, 10, 13, 10, 45, 0, tz="UTC"),
    catchup=False,
    tags=['half hourly'],
    default_args={
        'retries': 2,
        'retry_delay': pendulum.duration(minutes=5),
    },
    params={
        "date_from": Param(default=DEFAULT_DATE, type="string", format='date-time', description='Date From'),
        "date_to": Param(default=DEFAULT_DATE, type="string", format='date-time', description='Date To'),
    },
    description='A ETL DAG for sync Actual or estimated wind and solar power generation data from API to PostgreSQL',
)
def power_data_sync() -> None:
    """ETL DAG for power data."""

    @task(task_display_name="Parameterize the dates")
    def parameterize(params: dict[str, Any], dag_run: DagRun) -> dict[str, Any]:
        """Validate the dates and return valid dates or raise an exception."""
        # Get the user inputs or system generated DAG run date
        date_from = params["date_from"]
        date_to = params["date_to"]

        # System generated DAG run
        if not dag_run.external_trigger:
            date_param = Helper.date_param(dag_run.logical_date)
            return {"date_from": date_param, "date_to": date_param}

        # Validate the user inputs
        valid = Validator(date_from, date_to)
        if valid.validate():
            return {"date_from": Helper.floored_to_30_min(valid.date_from), "date_to": Helper.floored_to_30_min(valid.date_to)}
        else:
            logger.error(valid.errors[-1])
            return {}

    @task(task_display_name="Create destination table if it doesn't exist")
    def table() -> None:
        """Create the destination table if it doesn't exist."""
        try:
            Destination().table_maintenance()
            logger.info("Table create successful")
        except Exception as e:
            logger.critical(f"Table create failed: {e}")

    @task(task_display_name="Fetch data from API")
    def fetch(p: dict[str, str]) -> dict[str, Any]:
        """Fetch the JSON data from the API and push it to XCom for downstream tasks."""
        try:
            # Fetch JSON data from the API
            data = Source().fetch_json(cast(pendulum.DateTime, p["date_from"]), cast(pendulum.DateTime, p["date_to"]))
            logger.info("Data fetch successful")

            return data

        except Exception as e:
            logger.critical(f"Data fetch failed: {e}")
            return {}

    @task(task_display_name="Transform data according to requirements")
    def transform(data: dict[str, Any]) -> list[tuple[str, str, float]]:
        """Transform the JSON data into a format suitable for bulk insert into the destination table."""
        if not data:
            logger.warning("No data to transform.")
            return []

        return Helper.transform(data)

    @task(task_display_name="Sync data to destination table")
    def sync(data: list[tuple[str, str, float]]) -> None:
        """Perform the bulk insert of the JSON data into the destination table."""
        if not data:
            logger.warning("No data to sync.")
            return
        try:
            Destination().bulk_sync(data)
            logger.info("Data sync successful")

        except Exception as e:
            logger.critical(f"Data sync failed: {e}")

    # Ignore the type hinting as dag dynamically generates handle xcom
    p = parameterize() # type: ignore
    fetch_data = fetch(p) # type: ignore
    data = transform(fetch_data) # type: ignore
    sync(data) # type: ignore

    table() >> p

# Instantiate the DAG
power_data_sync()
