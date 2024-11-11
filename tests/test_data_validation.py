from typing import Any
from validation.data_validation import DataValidator


class TestDataValidator:
    """Test the parameter validator class."""

    def test_data_validator(self, mock_data: dict[str, list[dict[str, Any]]]) -> None:
        """Run the validation and check if it passes."""
        assert DataValidator(mock_data["data"]).validate(), "Data validation did not pass.my"
