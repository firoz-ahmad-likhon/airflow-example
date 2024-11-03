import great_expectations as gx
import pandas as pd
import logging
from .validator import Validator
from great_expectations.core import ExpectationValidationResult, ExpectationSuiteValidationResult


class DataValidator(Validator):
    """Class to validate data using great_expectations library."""

    def __init__(self, data: list[tuple[str, str, float]]):
        """"Initialize data validator with data."""
        try:
            self.df = pd.DataFrame(data)
        except Exception as e:
            logging.error(f"Error while converting data to pandas dataframe: {e}")

    def validate(self) -> ExpectationValidationResult | ExpectationSuiteValidationResult:
        """"Validate data using great_expectations library."""
        context = gx.get_context()
        data_source = context.data_sources.add_pandas("pandas")
        data_asset = data_source.add_dataframe_asset(name="pd dataframe asset")

        batch_definition = data_asset.add_batch_definition_whole_dataframe("batch definition")
        batch = batch_definition.get_batch(batch_parameters={"dataframe": self.df})

        expectation = gx.expectations.ExpectTableRowCountToEqual(
            value=3,
        )

        return batch.validate(expectation)
