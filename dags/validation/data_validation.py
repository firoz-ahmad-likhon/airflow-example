import os
from typing import Any, cast
import great_expectations as gx
import pendulum
from great_expectations import RunIdentifier
import pandas as pd
from .validator import Validator
import logging

class DataValidator(Validator):
    """Class to validate data using great_expectations library."""

    def __init__(self, data: list[dict[str, Any]]):
        """"Initialize data validator with data."""
        try:
            self.df = pd.DataFrame(data)
        except Exception as e:
            logging.error(f"Error while converting data to pandas dataframe: {e}")

        # Define the project directory
        project_dir = os.path.join(os.environ['AIRFLOW_HOME'], "quality")
        # Get the Great Expectations context
        self.context = gx.get_context(mode="file", project_root_dir=project_dir)

    def validate(self) -> bool:
        """"Validate data using great_expectations library."""
        # Define the run name and time.
        run_id = RunIdentifier(run_name="Quality", run_time=pendulum.now('UTC').strftime('%Y%m%dT%H%M%S.%f'))
        # Run the statistical checkpoints
        statistical_result = self.context.checkpoints.get("statistical_checkpoint").run(
            batch_parameters={"dataframe": self.df}, run_id=run_id,
        )
        # Run the completeness checkpoints
        completeness_result = self.context.checkpoints.get("completeness_checkpoint").run(
            batch_parameters={"dataframe": self.df}, run_id=run_id,
        )

        return cast(bool, statistical_result.success and completeness_result.success)

    def doc(self) -> None:
        """Build the Data Docs."""
        self.context.build_data_docs()
        # Print out the docs URL
        logging.info(f"Data Docs available at: {self.context.get_docs_sites_urls()[0]['site_url']}")
