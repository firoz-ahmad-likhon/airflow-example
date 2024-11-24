import pytest
from validation.parameter_validation import ParameterValidator


@pytest.fixture(scope='class')
def parameter_validator() -> ParameterValidator:
    """Initialize the ParameterValidator."""
    return ParameterValidator("2024-10-15 00:00", "2024-10-16 00:30")

@pytest.fixture(scope='class')
def parameter_validator_with_invalid_dates() -> ParameterValidator:
    """Initialize the ParameterValidator."""
    return ParameterValidator("invalid", "2024-10-16 00:30")
