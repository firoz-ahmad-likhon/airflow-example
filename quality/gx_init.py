import argparse
import os
import shutil
import great_expectations as gx


class GXInitiator:
    """Initialize the Great Expectations context and add data assets, suites, validation definitions and checkpoints."""

    # Define constants
    PROJECT_DIR = os.path.join(os.environ['AIRFLOW_HOME'], "quality")
    GX_DIR = os.path.join(PROJECT_DIR, "gx")
    SOURCE_NAME = "pandas"
    ASSET_NAME = "psr"
    BATCH_NAME = "psr batch"
    INGESTION_TIME_SITE_NAME = "ingestion_time_site"
    DOC_BASE_DIR_INGESTION_TIME = "uncommitted/data_docs/" + INGESTION_TIME_SITE_NAME + "/"
    ACTIONS = [
        gx.checkpoint.actions.UpdateDataDocsAction(
            name="Automatically data docs generation",
            site_names=[INGESTION_TIME_SITE_NAME],
        ),
    ]

    @classmethod
    def initialize(cls, mode: str) -> None:
        """Initialize the Great Expectations context based on the provided mode.

        Args:
            mode (str): Mode for initializing the context. It can be either:
                - 'recreate': To re-initialize the context.
                - 'init': To initialize a new context.

        """
        # Check mode and delete project directory if mode=recreate
        if mode == "recreate" and os.path.exists(cls.GX_DIR):
            shutil.rmtree(cls.GX_DIR)  # Delete the directory and all its contents

        # Initialize context only if the project directory does not exist
        if not os.path.exists(cls.GX_DIR):
            cls.context = gx.get_context(mode="file", project_root_dir=cls.PROJECT_DIR)
            cls.context.enable_analytics(enable=False)
            cls.add_data_docs_site()
            cls.add_validation_results_store_backend()
            cls.add_data_assets()
            cls.add_suites_and_validation_definitions()
            cls.add_checkpoint()

    @classmethod
    def add_data_docs_site(cls) -> None:
        """Add ingestion time data docs site to the data context."""
        cls.context.add_data_docs_site(
            site_name=cls.INGESTION_TIME_SITE_NAME,
            site_config={
                "class_name": "SiteBuilder",
                "site_index_builder": {
                    "class_name": "DefaultSiteIndexBuilder",
                },
                "store_backend": {
                    "class_name": "TupleFilesystemStoreBackend",
                    "base_directory": cls.DOC_BASE_DIR_INGESTION_TIME,
                },
            },
        )

    @classmethod
    def add_validation_results_store_backend(cls) -> None:
        """Configure a database store for storing validation results."""
        cls.context.add_store("validation_results_store", {
            "class_name": "ValidationResultsStore",
            "store_backend": {
                "class_name": "DatabaseStoreBackend",
                "url": os.environ['GX_POSTGRES_CONNECTION_STRING'],
                "table_name": os.environ['GX_TABLE_NAME'],
            },
        })

    @classmethod
    def add_data_assets(cls) -> None:
        """Add data assets and batch definition to the data context."""
        # Add a pandas datasource
        data_source = cls.context.data_sources.add_pandas(name=cls.SOURCE_NAME)

        # Add a DataFrame asset for power
        data_asset = data_source.add_dataframe_asset(name=cls.ASSET_NAME)

        # Add a Batch Definition to the Data Asset
        cls.batch_definition = data_asset.add_batch_definition_whole_dataframe(
            cls.BATCH_NAME,
        )

    @classmethod
    def add_suites_and_validation_definitions(cls) -> None:
        """Add suites and validation definitions to the data context."""
        cls.distribution_suite()
        cls.missingness_suite()
        cls.schema_suite()
        cls.volume_suite()

    @classmethod
    def distribution_suite(cls) -> None:
        """Define statistical expectation suite to the data context."""
        # Define an expectation suite
        suite = cls.context.suites.add(gx.ExpectationSuite(name="distribution"))

        # Add expectations to the suite
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToBeBetween(column="settlementPeriod", min_value=1, max_value=48),
        )
        # Create a Validation Definition and Add to the Data Context
        cls.context.validation_definitions.add(gx.ValidationDefinition(
            data=cls.batch_definition, suite=suite, name="distribution",
        ))

    @classmethod
    def missingness_suite(cls) -> None:
        """Define completeness expectation suite to the data context."""
        suite = cls.context.suites.add(gx.ExpectationSuite(name="missingness"))

        # Add expectations to the suite
        suite.add_expectation(
            gx.expectations.ExpectColumnValuesToNotBeNull(column="psrType"),
        )

        # Create a Validation Definition and Add to the Data Context
        cls.context.validation_definitions.add(gx.ValidationDefinition(
            data=cls.batch_definition, suite=suite, name="missingness",
        ))

    @classmethod
    def schema_suite(cls) -> None:
        """Define validity expectation suite to the data context."""
        suite = cls.context.suites.add(gx.ExpectationSuite(name="schema"))

        # Add expectations to the suite
        suite.add_expectation(
            gx.expectations.ExpectColumnToExist(column="settlementDate"),
        )
        suite.add_expectation(
            gx.expectations.ExpectTableColumnCountToEqual(value=7),
        )

        # Create a Validation Definition and Add to the Data Contex
        cls.context.validation_definitions.add(gx.ValidationDefinition(
            data=cls.batch_definition, suite=suite, name="schema",
        ))

    @classmethod
    def volume_suite(cls) -> None:
        """Define volume expectation suite to the data context."""
        suite = cls.context.suites.add(gx.ExpectationSuite(name="volume"))

        # Add expectations to the suite
        suite.add_expectation(
            gx.expectations.ExpectTableRowCountToBeBetween(min_value=0, max_value=1008),
        )

        # Create a Validation Definition and Add to the Data Context
        cls.context.validation_definitions.add(gx.ValidationDefinition(
            data=cls.batch_definition, suite=suite, name="volume",
        ))

    @classmethod
    def add_checkpoint(cls) -> None:
        """Add checkpoints to the data context."""
        cls.statistical_checkpoint()
        cls.completeness_checkpoint()

    @classmethod
    def statistical_checkpoint(cls) -> None:
        """Define statistical checkpoint to the data context."""
        cls.context.checkpoints.add(gx.Checkpoint(
            name="statistical_checkpoint",
            validation_definitions=[
                cls.context.validation_definitions.get("distribution"),
            ],
            actions=cls.ACTIONS,
        ))

    @classmethod
    def completeness_checkpoint(cls) -> None:
        """Define completeness, validity and volume checkpoint to the data context."""
        cls.context.checkpoints.add(gx.Checkpoint(
            name="completeness_checkpoint",
            validation_definitions=[
                cls.context.validation_definitions.get("missingness"),
                cls.context.validation_definitions.get("schema"),
                cls.context.validation_definitions.get("volume"),
            ],
            actions=cls.ACTIONS,
        ))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize Great Expectations context.")
    parser.add_argument("--mode", choices=["recreate", "init"], default="init",
                        help="Specify whether to recreate the project directory or leave it as is.")
    args = parser.parse_args()

    GXInitiator.initialize(mode=args.mode)
