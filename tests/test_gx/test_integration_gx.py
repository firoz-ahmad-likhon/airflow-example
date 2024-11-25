from great_expectations.data_context import AbstractDataContext
from gx_init import GXInitiator


class TestIntegrationGX:
    """Integration tests for context."""

    def test_project_directory_exists(self, gxi: type[GXInitiator]) -> None:
        """Assert that the Great Expectations project directory exists."""
        assert gxi.GX_DIR.exists(), "GX directory should be created"

    def test_context_initialized(self, context: AbstractDataContext) -> None:
        """Assert that the Great Expectations context is initialized."""
        assert context is not None, "Context should be successfully initialized"

    def test_doc_site_added(self, gxi: type[GXInitiator], context: AbstractDataContext) -> None:
        """Assert that the doc site is added to the context."""
        assert gxi.INGESTION_TIME_SITE_NAME in context.list_data_docs_sites(), "Ingestion time site should exist in data docs sites"

    def test_validation_results_store_configured(self, context: AbstractDataContext) -> None:
        """Assert that the validation results store is configured."""
        any(store['name'] == 'validation_results_store' for store in context.list_stores()), "Validation results store should be configured"

    def test_data_sources_added(self, gxi: type[GXInitiator], context: AbstractDataContext) -> None:
        """Assert that the data source is added to the context."""
        assert gxi.SOURCE_NAME in context.data_sources.all(), "Data source should be added to the context"

    def test_data_assets_added(self, gxi: type[GXInitiator], context: AbstractDataContext) -> None:
        """Assert that the asset is added to the context."""
        assert {gxi.SOURCE_NAME: [gxi.ASSET_NAME]} == context.get_available_data_asset_names(datasource_names=[gxi.SOURCE_NAME]), "Data asset should be added to the data source"

    def test_expectation_suites(self, context: AbstractDataContext, dimensions: list[str]) -> None:
        """Assert that all expectation suites exist in the context."""
        gx_suites = [suite.name for suite in context.suites.all()]
        for suite in dimensions:
            assert suite in gx_suites, f"Expectation suite '{suite}' should exist"

    def test_validation_definitions(self, context: AbstractDataContext, dimensions: list[str]) -> None:
        """Assert that all validation definitions are added to the context."""
        gx_validation_def = set(validation.name for validation in context.validation_definitions.all())
        assert gx_validation_def == set(dimensions), "All validation definitions should be added to the context"

    def test_checkpoints(self, context: AbstractDataContext, checkpoints: list[str]) -> None:
        """Assert that all checkpoints are added to the context."""
        gx_checkpoints = [checkpoint.name for checkpoint in context.checkpoints.all()]
        for checkpoint in checkpoints:
            assert checkpoint in gx_checkpoints, f"Checkpoint '{checkpoint}' should exist"
