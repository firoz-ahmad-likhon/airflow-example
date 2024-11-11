from typing import Any, cast
import great_expectations as gx
from great_expectations import RunIdentifier
import pandas as pd
from .validator import Validator
from datetime import datetime, timezone
import logging

class DataValidator(Validator):
    """Class to validate data using great_expectations library."""

    def __init__(self, data: list[dict[str, Any]]):
        """"Initialize data validator with data."""
        try:
            self.df = pd.DataFrame(data)
        except Exception as e:
            logging.error(f"Error while converting data to pandas dataframe: {e}")

    def validate(self) -> bool:
        """"Validate data using great_expectations library."""
        # Get the Great Expectations context
        context = gx.get_context(mode="file", project_root_dir="./gx")

        run_id = RunIdentifier(run_name="Quality", run_time=datetime.now(tz=timezone.utc).strftime('%Y%m%dT%H%M%S.%f'))

        statistical_result = context.checkpoints.get("statistical_checkpoint").run(
            batch_parameters={"dataframe": self.df}, run_id=run_id,
        )

        completeness_result = context.checkpoints.get("completeness_checkpoint").run(
            batch_parameters={"dataframe": self.df}, run_id=run_id,
        )

        # Build the Data Docs
        context.build_data_docs()
        # Print out the docs URL
        logging.info(f"Data Docs available at: {context.get_docs_sites_urls()[0]['site_url']}")

        return cast(bool, statistical_result.success and completeness_result.success)
