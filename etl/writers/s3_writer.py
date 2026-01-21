"""
S3 writer with partition strategies for data lake storage.

Writes DataFrames to S3 in Parquet format with optimized partitioning.
"""

from typing import Optional
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, year, month, dayofmonth, lit
from datetime import datetime


class S3Writer:
    """
    S3 Parquet writer with intelligent partitioning strategies.

    Supports:
    - Date-based partitioning (year/month/day from data column)
    - Load date partitioning (partition by ETL execution date)
    - Overwrite and append modes
    - Small file coalescing
    """

    def __init__(self, s3_bucket: str, s3_prefix: str):
        """
        Initialize S3 writer.

        Args:
            s3_bucket: S3 bucket name
            s3_prefix: Prefix/path within bucket (e.g., 'raw/retail_db')
        """
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix.strip("/")

    def _get_s3_path(self, table_name: str) -> str:
        """
        Get base S3 path for a table.

        Args:
            table_name: Name of the table

        Returns:
            S3 path (e.g., s3a://bucket/prefix/table_name/)
        """
        return f"s3a://{self.s3_bucket}/{self.s3_prefix}/{table_name}"

    def write_with_date_partition(
        self, df: DataFrame, table_name: str, date_column: str, mode: str = "append"
    ):
        """
        Write DataFrame with date-based partitioning (year/month/day).

        Extracts year, month, day from the specified date column and
        partitions data accordingly for query efficiency.

        Args:
            df: DataFrame to write
            table_name: Name of the table
            date_column: Column containing date/timestamp for partitioning
            mode: Write mode ('overwrite' or 'append')
        """
        s3_path = self._get_s3_path(table_name)

        # Add partition columns
        df_with_partitions = (
            df.withColumn("year", year(col(date_column)))
            .withColumn("month", month(col(date_column)))
            .withColumn("day", dayofmonth(col(date_column)))
        )

        # Coalesce to avoid small files (aim for ~128MB files)
        # Adjust based on data size
        num_partitions = max(1, df.rdd.getNumPartitions() // 4)
        df_coalesced = df_with_partitions.coalesce(num_partitions)

        # Write to S3
        (
            df_coalesced.write.mode(mode)
            .partitionBy("year", "month", "day")
            .parquet(s3_path)
        )

    def write_with_load_date_partition(
        self, df: DataFrame, table_name: str, mode: str = "overwrite"
    ):
        """
        Write DataFrame with load_date partitioning.

        Partitions data by the ETL execution date (today).
        Typically used for full refresh tables.

        Args:
            df: DataFrame to write
            table_name: Name of the table
            mode: Write mode ('overwrite' or 'append')
        """
        s3_path = self._get_s3_path(table_name)

        # Add load_date partition column (current date)
        load_date = datetime.now().strftime("%Y-%m-%d")
        df_with_partition = df.withColumn("load_date", lit(load_date))

        # Coalesce to avoid small files
        num_partitions = max(1, df.rdd.getNumPartitions() // 4)
        df_coalesced = df_with_partition.coalesce(num_partitions)

        # Write to S3
        (df_coalesced.write.mode(mode).partitionBy("load_date").parquet(s3_path))

    def write_with_strategy(
        self,
        df: DataFrame,
        table_name: str,
        partition_strategy: str,
        date_column: Optional[str] = None,
        load_type: str = "full",
    ):
        """
        Write DataFrame using specified partition strategy.

        Args:
            df: DataFrame to write
            table_name: Name of the table
            partition_strategy: Partitioning strategy ('date' or 'load_date')
            date_column: Date column for date-based partitioning
            load_type: Loading strategy ('full', 'id_incremental', 'date_incremental')

        Raises:
            ValueError: If invalid partition_strategy or missing required parameters
        """
        if partition_strategy == "date":
            if not date_column:
                raise ValueError("date partition strategy requires date_column")

            # Date-based partitioning always uses append mode
            self.write_with_date_partition(df, table_name, date_column, mode="append")

        elif partition_strategy == "load_date":
            # Determine write mode based on load type
            # Full refresh: overwrite
            # Incremental: append
            mode = "overwrite" if load_type == "full" else "append"
            self.write_with_load_date_partition(df, table_name, mode=mode)

        else:
            raise ValueError(
                f"Invalid partition_strategy: {partition_strategy}. "
                f"Must be 'date' or 'load_date'"
            )
