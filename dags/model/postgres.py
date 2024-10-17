import logging
import os
import psycopg2
from psycopg2 import extras
from psycopg2._psycopg import connection
from collections.abc import Sequence
from typing import Any


class PostgresSQL:
    """The class is responsible for database connection and operations."""

    instance = None

    def __new__(cls) -> 'PostgresSQL':
        """Ensure only one instance of PostgresSQL class is created."""
        if not cls.instance:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        """Initialize PostgresSQL class."""
        self.connection = None

    def connect(self) -> connection:
        """Establish connection with PostgresSQL database.

        If the connection already exists, return the existing connection.
        """
        if not self.connection:
            try:
                self.connection = psycopg2.connect(os.environ['POSTGRES_CONNECTION_STRING'])
            except psycopg2.Error as e:
                logging.error("Error connecting to database:" + str(e))
        return self.connection

    def disconnect(self) -> None:
        """Disconnect the connection with PostgresSQL database."""
        if self.connection is not None and self.connection.closed == 0:
            self.connection.close()

    def query(self, query: str) -> None:
        """Run a query.

        @param query: sql query
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            self.connection.commit()

    def bulk_insert(self, query: str, data: Sequence[Any]) -> None:
        """Run a batch insert.

        @param query: sql query
        @param data: list of tuples of data
        """
        with self.connection.cursor() as cursor:
            extras.execute_values(cursor, query, data)
            self.connection.commit()

    def fetch(self, query: str) -> list[tuple[Any, ...]] | Any:
        """Acquire data.

        @param query: sql query
        @return: list of tuples of data
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)

            return cursor.fetchall()

    def single(self, query: str) -> tuple[Any, ...] | Any:
        """Acquire data.

        @param query: sql query
        @return: tuple of data
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query)

            return cursor.fetchone()
