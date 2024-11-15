import logging
import pendulum
from typing import Any, cast

from airflow.exceptions import AirflowException
from airflow.utils.edgemodifier import Label
from airflow.utils.trigger_rule import TriggerRule
from airflow.decorators import dag, task, task_group
from airflow.models.param import Param
from airflow.models import DagRun

from model.destination import DestinationPostgreSQL as Destination
from model.source import SourceAPI as Source
from helper.api_helper import APIHelper as Helper
from validation.parameter_validation import ParameterValidator as Validator
from validation.data_validation import DataValidator

# Use the Airflow task logger
logger = logging.getLogger("airflow.task")

# Default date to identify the logical DAG run
DEFAULT_DATE = pendulum.now(tz="UTC").to_iso8601_string()


@dag(
    schedule='*/30 * * * *',  # Run every 30 minutes
    start_date=pendulum.datetime(2024, 10, 13, 10, 45, 0, tz="UTC"),
    catchup=False,
    tags=['half hourly'],
    default_args={
        'retries': 1,
        'retry_delay': pendulum.duration(minutes=5),
    },
    params={
        "date_from": Param(default=DEFAULT_DATE, type="string", format='date-time', description='Date From'),
        "date_to": Param(default=DEFAULT_DATE, type="string", format='date-time', description='Date To'),
    },
    description='A ETL DAG for sync Actual or estimated wind and solar power generation data from API to PostgreSQL',
)
def psr_sync() -> None:
    """ETL DAG for power data."""

    @task(task_display_name="Parameterize the dates", retries=0)
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
            return {"date_from": Helper.floored_to_30_min(valid.date_from),
                    "date_to": Helper.floored_to_30_min(valid.date_to)}
        else:
            raise AirflowException(valid.errors[-1])

    @task_group(group_id="Processor", tooltip="Data processing unit")
    def source(parameters: dict[str, str]) -> Any:
        """Tasks group for processing source data."""
        @task(task_display_name="Fetcher")
        def fetch(p: dict[str, str]) -> dict[str, Any]:
            """Fetch the JSON data from the API and push it to XCom for downstream tasks."""
            try:
                data = Source().fetch_json(cast(pendulum.DateTime, p["date_from"]), cast(pendulum.DateTime, p["date_to"]))

                if not data["data"]:
                    raise AirflowException("Data is empty")
                logger.info("Data fetch successful")
                return data
            except Exception as e:
                raise AirflowException(f"Data fetch failed: {e}") from e

        @task(task_display_name="Validator")
        def validate(data: dict[str, Any]) -> dict[str, Any]:
            """Validate the data before transformation."""
            q = DataValidator(data["data"])
            result = q.validate()
            q.doc()  # Generate documentation

            if result:
                logger.info("Data validation successful")
                return data
            else:
                raise AirflowException("Data validation failed")

        @task(task_display_name="Transformer")
        def transform(data: dict[str, Any]) -> list[tuple[str, str, float]]:
            """Transform the JSON data into a format suitable for bulk insert into the destination table."""
            return Helper.transform(data)

        fetched_data = fetch(parameters)
        validated_data = validate(cast(dict[str, Any], fetched_data))
        transformed_data = transform(cast(dict[str, Any], validated_data))

        fetched_data >> Label("Fetched data from API") >> validated_data >> Label("Validated data") >> transformed_data >> Label("Transformed data")

        return transformed_data

    @task(task_display_name="Sync data to destination table")
    def sync(data: list[tuple[str, str, float]]) -> bool:
        """Perform the bulk insert of the JSON data into the destination table."""
        try:
            Destination().table_maintenance()  # Create the destination table if it doesn't exist.
            Destination().bulk_sync(data)
            logger.info("Data sync successful")
            return True
        except Exception as e:
            raise AirflowException(f"Data sync failed: {e}") from e

    @task(trigger_rule=TriggerRule.ONE_FAILED, retries=0)
    def watcher() -> None:
        """Raise an exception if one or more upstream tasks failed."""
        raise AirflowException("Failing task because one or more upstream tasks failed.")

    # Set up dependencies for TaskGroups and tasks
    parameterized = parameterize()  # type: ignore
    fetched = source(cast(dict[str, str], parameterized))
    synced = sync(cast(list[tuple[str, str, float]], fetched))

    fetched >> Label("Transformed data") >> synced

    [parameterized, fetched, synced] >> Label("Fail") >> watcher()

# Instantiate the DAG
psr_sync()
