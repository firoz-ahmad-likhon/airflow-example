from model.destination import DestinationPostgreSQL

class TestDestination:
    """Test the Destination class."""

    def test_bulk_sync(self, destination: DestinationPostgreSQL) -> None:
        """Test bulk_sync method to insert data into the database.

        :param destination: The destination object from fixture.
        """
        data = [
            ('bmreports, Wind Onshore, min30', '2023-07-21T04:30:00Z', 640.283),
            ('bmreports, Wind Offshore, min30', '2023-07-21T04:30:00Z', 77.014),
            ('bmreports, Solar, min30', '2023-07-21T04:30:00Z', 89.0),
        ]

        # Insert mock data
        inserted_count = destination.bulk_sync(data)

        # Verify data count
        assert inserted_count == len(data), "Not all data was inserted"

    def test_bulk_sync_conflict_resolution(self, destination: DestinationPostgreSQL) -> None:
        """Test conflict resolution when inserting data into the database.

        :param destination: The destination object from fixture.
        """
        data = [
            ('bmreports, Wind Onshore, min30', '2023-07-21T04:30:00Z', 740.283),
            ('bmreports, Wind Offshore, min30', '2023-07-21T04:30:00Z', 87.014),
            ('bmreports, Solar, min30', '2023-07-21T04:30:00Z', 89.0),
        ]

        # Insert mock data
        inserted_count = destination.bulk_sync(data)

        # Verify data count
        assert inserted_count == len(data), "Not all data was inserted"
        result = destination.single(
            f"SELECT value FROM {destination.TABLE_NAME} WHERE curve_name='bmreports, Wind Onshore, min30' AND curve_date='2023-07-21T04:30:00Z';")
        expected_value = 740.283
        assert float(result[0]) == expected_value, "Conflict resolution did not update value correctly"
