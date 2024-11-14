from typing import cast
import pendulum
from .validator import Validator


class ParameterValidator(Validator):
    """Validate parameters for the API call.

    - To validate the date the date_form and date_to must be the instance of pendulum.DateTime.
    """

    def __init__(self, date_from: str, date_to: str):
        """Initialize the class with the date_from and date_to parameters.

        :param date_from: The start date time of the time period.
        :param date_to: The end date time of the time period.
        """
        self.errors: list[str] = []

        try:
            self.date_from: pendulum.DateTime = cast(pendulum.DateTime, pendulum.parse(date_from))
            self.date_to: pendulum.DateTime = cast(pendulum.DateTime, pendulum.parse(date_to))
        except ValueError:
            self.errors.append("Expected format is 'YYYY-MM-DD HH:MM'.")


    def validate_minutes(self) -> bool:
        """Ensure minutes are either 00 or 30."""
        if self.date_from.minute not in [0, 30]:
            self.errors.append("Minutes must be either 00 or 30.")

            return False

        if self.date_to.minute not in [0, 30]:
            self.errors.append("Minutes must be either 00 or 30.")

            return False

        return True

    def validate_date_order(self) -> bool:
        """Ensure that date_from is before or equal to date_to."""
        if self.date_from > self.date_to:
            self.errors.append("From date must be before or equal to To date.")

            return False

        return True

    def validate_days_range(self, max_days: int = 7) -> bool:
        """Check the date range is within the allowed limit.

        :param max_days: The maximum number of days allowed. Default is 7.
        """
        if self.date_to.diff(self.date_from).in_days() > max_days:
            self.errors.append(f"Date range should not exceed {max_days} days.")

            return False

        return True

    def validate(self) -> bool:
        """Aggregate validation steps and return True or False."""
        if len(self.errors) > 0:  # As string to date conversion can raise error first.
            return False
        # if not self.validate_minutes():
        #     return False

        if not self.validate_date_order():
            return False

        if not self.validate_days_range():
            return False

        return True
