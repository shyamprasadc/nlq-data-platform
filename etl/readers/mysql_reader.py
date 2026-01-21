"""
MySQL reader with support for full and incremental loading strategies.

Reads data from MySQL using Spark JDBC with optimizations for performance.
"""

import os
from typing import Optional, Dict, Any
from pyspark.sql import SparkSession, DataFrame


class MySQLReader:
    """
    MySQL JDBC reader with support for multiple loading strategies.

    Supports:
    - Full table reads
    - ID-based incremental reads (WHERE id > last_max_id)
    - Date-based incremental reads (WHERE date > last_timestamp)
    """

    def __init__(self, spark: SparkSession):
        """
        Initialize MySQL reader.

        Args:
            spark: Active SparkSession
        """
        self.spark = spark
        self.jdbc_url = self._build_jdbc_url()
        self.connection_properties = self._get_connection_properties()

    def _build_jdbc_url(self) -> str:
        """
        Build JDBC URL from environment variables.

        Returns:
            JDBC connection string

        Raises:
            ValueError: If required environment variables are missing
        """
        host = os.getenv("MYSQL_HOST")
        port = os.getenv("MYSQL_PORT", "3306")
        database = os.getenv("MYSQL_DATABASE")

        if not host or not database:
            raise ValueError(
                "Missing required environment variables: MYSQL_HOST, MYSQL_DATABASE"
            )

        return f"jdbc:mysql://{host}:{port}/{database}"

    def _get_connection_properties(self) -> Dict[str, str]:
        """
        Get JDBC connection properties from environment variables.

        Returns:
            Dictionary of connection properties

        Raises:
            ValueError: If required credentials are missing
        """
        user = os.getenv("MYSQL_USER")
        password = os.getenv("MYSQL_PASSWORD")

        if not user or not password:
            raise ValueError(
                "Missing required environment variables: MYSQL_USER, MYSQL_PASSWORD"
            )

        return {
            "user": user,
            "password": password,
            "driver": "com.mysql.cj.jdbc.Driver",
            # Performance optimizations
            "fetchsize": "10000",  # Rows to fetch per round trip
            "zeroDateTimeBehavior": "convertToNull",  # Handle invalid dates
        }

    def read_full_table(self, table_name: str, num_partitions: int = 4) -> DataFrame:
        """
        Read entire table from MySQL.

        Args:
            table_name: Name of the table to read
            num_partitions: Number of Spark partitions for parallel reading

        Returns:
            DataFrame containing all table data
        """
        return (
            self.spark.read.format("jdbc")
            .option("url", self.jdbc_url)
            .option("dbtable", table_name)
            .option("numPartitions", num_partitions)
            .options(**self.connection_properties)
            .load()
        )

    def read_id_incremental(
        self, table_name: str, id_column: str, last_max_id: int, num_partitions: int = 4
    ) -> DataFrame:
        """
        Read table incrementally based on ID column.

        Args:
            table_name: Name of the table to read
            id_column: Name of the ID column for incremental loading
            last_max_id: Last maximum ID processed (exclusive)
            num_partitions: Number of Spark partitions for parallel reading

        Returns:
            DataFrame containing rows where id > last_max_id
        """
        # Build query for incremental read
        query = f"(SELECT * FROM {table_name} WHERE {id_column} > {last_max_id}) AS incremental_data"

        return (
            self.spark.read.format("jdbc")
            .option("url", self.jdbc_url)
            .option("dbtable", query)
            .option("numPartitions", num_partitions)
            .options(**self.connection_properties)
            .load()
        )

    def read_date_incremental(
        self,
        table_name: str,
        date_column: str,
        last_timestamp: str,
        num_partitions: int = 4,
    ) -> DataFrame:
        """
        Read table incrementally based on date/timestamp column.

        Args:
            table_name: Name of the table to read
            date_column: Name of the date/timestamp column
            last_timestamp: Last timestamp processed (exclusive), format: 'YYYY-MM-DD HH:MM:SS'
            num_partitions: Number of Spark partitions for parallel reading

        Returns:
            DataFrame containing rows where date > last_timestamp
        """
        # Build query for date-based incremental read
        query = (
            f"(SELECT * FROM {table_name} "
            f"WHERE {date_column} > '{last_timestamp}') AS incremental_data"
        )

        return (
            self.spark.read.format("jdbc")
            .option("url", self.jdbc_url)
            .option("dbtable", query)
            .option("numPartitions", num_partitions)
            .options(**self.connection_properties)
            .load()
        )

    def read_with_strategy(
        self,
        table_name: str,
        load_type: str,
        incremental_column: Optional[str] = None,
        last_checkpoint: Optional[Any] = None,
        num_partitions: int = 4,
    ) -> DataFrame:
        """
        Read table using specified loading strategy.

        Args:
            table_name: Name of the table to read
            load_type: Loading strategy ('full', 'id_incremental', 'date_incremental')
            incremental_column: Column name for incremental loading
            last_checkpoint: Last checkpoint value (int for ID, str for date)
            num_partitions: Number of Spark partitions

        Returns:
            DataFrame with requested data

        Raises:
            ValueError: If invalid load_type or missing required parameters
        """
        if load_type == "full":
            return self.read_full_table(table_name, num_partitions)

        elif load_type == "id_incremental":
            if not incremental_column or last_checkpoint is None:
                raise ValueError(
                    "id_incremental requires incremental_column and last_checkpoint"
                )
            return self.read_id_incremental(
                table_name, incremental_column, int(last_checkpoint), num_partitions
            )

        elif load_type == "date_incremental":
            if not incremental_column or not last_checkpoint:
                raise ValueError(
                    "date_incremental requires incremental_column and last_checkpoint"
                )
            return self.read_date_incremental(
                table_name, incremental_column, str(last_checkpoint), num_partitions
            )

        else:
            raise ValueError(
                f"Invalid load_type: {load_type}. "
                f"Must be 'full', 'id_incremental', or 'date_incremental'"
            )
