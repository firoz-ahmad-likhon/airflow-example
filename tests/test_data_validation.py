from validation.data_validation import DataValidator


class TestDataValidator:
    """Test the parameter validator class."""

    def test_data_validator(self, data_validator: DataValidator) -> None:
        """Run the validation and check if it passes."""
        validation_result = data_validator.validate()

        # Assert that the validation result is successful
        assert validation_result["success"], "Data validation did not pass.my"