from typing import cast

import pytest
import great_expectations as gx
from _pytest.tmpdir import TempPathFactory
from great_expectations.data_context import AbstractDataContext
from gx_init import GXInitiator


@pytest.fixture(scope="session")
def gxi(tmp_path_factory : TempPathFactory) -> type[GXInitiator]:
    """Fixture to initialize a GX context for integration tests.

    This fixture sets up the necessary directories and initializes
    the Great Expectations context using `GXInitiator`.

    Args:
        tmp_path_factory (TempPathFactory): A temporary directory provided by pytest.

    Returns:
        The `GXInitiator` class.

    """
    # Use tmp_path_factory to create a session-scoped temporary directory
    session_tmp_path = tmp_path_factory.mktemp("session_quality")
    GXInitiator.PROJECT_DIR = session_tmp_path / "quality"
    GXInitiator.GX_DIR = GXInitiator.PROJECT_DIR / "gx"

    # Initialize Great Expectations
    GXInitiator.initialize("init")

    return cast(type[GXInitiator], GXInitiator)


@pytest.fixture(scope="session")
def context(gxi: GXInitiator) -> AbstractDataContext:
    """Fixture to provide an AbstractDataContext for integration tests.

    This fixture uses the directory set up by the `gxi` fixture.

    Args:
        gxi: The GXInitiator fixture providing the project directory.

    Returns:
        A Great Expectations AbstractDataContext initialized with the project directory.

    """
    return gx.get_context(mode="file", project_root_dir=str(gxi.PROJECT_DIR)) # Use the directory set by `gxi`


@pytest.fixture(scope="session")
def dimensions() -> list[str]:
    """List of dimensions for suites, validation definitions.

    returns: A list of Great Expectations suites.
    """
    return ["distribution", "missingness", "schema", "volume"]


@pytest.fixture(scope="session")
def checkpoints() -> list[str]:
    """List of available checkpoints.

    returns: A list of Great Expectations checkpoints.
    """
    return ["statistical_checkpoint", "completeness_checkpoint"]
