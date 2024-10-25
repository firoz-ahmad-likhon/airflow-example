from .postgres import PostgresSQL


class DestinationPostgreSQL(PostgresSQL):
    """The class is intended to sync the API data to PostgreSQL."""

    TABLE_NAME = 'power_data'

    def __init__(self) -> None:
        """Initialize class."""
        super().__init__()

        self.connect()  # Instantiate a connection

    def table_maintenance(self) -> None:
        """Create table if it doesn't exist."""
        self.query(f"""
        CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
            curve_name VARCHAR(255),
            curve_date TIMESTAMP NOT NULL,
            value NUMERIC,
            PRIMARY KEY (curve_name, curve_date)
        );

        COMMENT ON TABLE {self.TABLE_NAME} IS 'Power generation data for different curves over time.';
        COMMENT ON COLUMN {self.TABLE_NAME}.curve_name IS 'The name of the curve, representing the type of power generation (e.g., solar, wind).';
        COMMENT ON COLUMN {self.TABLE_NAME}.curve_date IS 'Timestamp indicating the start_date, stored in UTC.';
        COMMENT ON COLUMN {self.TABLE_NAME}.value IS 'The measured value associated with the curve at the specified date and time.';
        """)


    def bulk_sync(self, data: list[tuple[str, str, float]]) -> int:
        """Insert data into the database.

        @param data: data
        """
        if data:
            # self.bulk_insert(f'INSERT INTO {self.TABLE_NAME} (curve_name, date, value) VALUES %s', data)
            self.bulk_insert(f"""
                INSERT INTO {self.TABLE_NAME} (curve_name, curve_date, value)
                VALUES %s
                ON CONFLICT (curve_name, curve_date)
                DO UPDATE SET value = EXCLUDED.value
            """, data)

        return len(data)
