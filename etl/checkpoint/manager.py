"""
Checkpoint and state management for incremental ETL loads.

Stores and retrieves checkpoint information in S3 for exactly-once processing.
"""

import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from pyspark.sql import SparkSession


class CheckpointManager:
    """
    Manages checkpoint state for incremental ETL loads.

    Checkpoints are stored in S3 as JSON files, one per table.
    Supports both ID-based and date-based checkpoints.
    """

    def __init__(self, spark: SparkSession, s3_checkpoint_path: str):
        """
        Initialize checkpoint manager.

        Args:
            spark: Active SparkSession
            s3_checkpoint_path: S3 path for checkpoint storage (e.g., s3a://bucket/checkpoints/)
        """
        self.spark = spark
        self.s3_checkpoint_path = s3_checkpoint_path.rstrip("/")

    def _get_checkpoint_path(self, table_name: str) -> str:
        """
        Get S3 path for table's checkpoint file.

        Args:
            table_name: Name of the table

        Returns:
            Full S3 path to checkpoint file
        """
        return f"{self.s3_checkpoint_path}/{table_name}.json"

    def get_checkpoint(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve checkpoint for a table.

        Args:
            table_name: Name of the table

        Returns:
            Checkpoint dictionary or None if no checkpoint exists

        Checkpoint structure:
            {
                "table_name": "orders",
                "last_checkpoint": "2024-01-20 15:30:00" or 12345,
                "last_updated": "2024-01-21T10:25:04+05:30",
                "row_count": 1500
            }
        """
        checkpoint_path = self._get_checkpoint_path(table_name)

        try:
            # Read checkpoint file from S3
            sc = self.spark.sparkContext
            hadoop_conf = sc._jsc.hadoopConfiguration()
            fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(
                sc._jvm.java.net.URI(checkpoint_path), hadoop_conf
            )
            path = sc._jvm.org.apache.hadoop.fs.Path(checkpoint_path)

            if not fs.exists(path):
                return None

            # Read file content
            input_stream = fs.open(path)
            content = ""
            reader = sc._jvm.java.io.BufferedReader(
                sc._jvm.java.io.InputStreamReader(input_stream)
            )

            line = reader.readLine()
            while line:
                content += line
                line = reader.readLine()

            reader.close()

            # Parse JSON
            checkpoint = json.loads(content)
            return checkpoint

        except Exception as e:
            # If checkpoint doesn't exist or can't be read, return None
            return None

    def save_checkpoint(self, table_name: str, last_checkpoint: Any, row_count: int):
        """
        Save checkpoint for a table.

        Args:
            table_name: Name of the table
            last_checkpoint: Checkpoint value (int for ID, str for date)
            row_count: Number of rows processed in this run
        """
        checkpoint_path = self._get_checkpoint_path(table_name)

        checkpoint_data = {
            "table_name": table_name,
            "last_checkpoint": last_checkpoint,
            "last_updated": datetime.now().isoformat(),
            "row_count": row_count,
        }

        # Convert to JSON
        json_content = json.dumps(checkpoint_data, indent=2)

        # Write to S3 using Spark
        sc = self.spark.sparkContext

        # Create RDD with single partition containing JSON
        rdd = sc.parallelize([json_content], 1)

        # Save to S3 (overwrite existing)
        rdd.saveAsTextFile(checkpoint_path + "_temp", compressionCodecClass=None)

        # Move temp file to final location
        hadoop_conf = sc._jsc.hadoopConfiguration()
        fs = sc._jvm.org.apache.hadoop.fs.FileSystem.get(
            sc._jvm.java.net.URI(checkpoint_path), hadoop_conf
        )

        temp_path = sc._jvm.org.apache.hadoop.fs.Path(
            checkpoint_path + "_temp/part-00000"
        )
        final_path = sc._jvm.org.apache.hadoop.fs.Path(checkpoint_path)

        # Delete existing checkpoint if exists
        if fs.exists(final_path):
            fs.delete(final_path, False)

        # Rename temp to final
        fs.rename(temp_path, final_path)

        # Clean up temp directory
        temp_dir = sc._jvm.org.apache.hadoop.fs.Path(checkpoint_path + "_temp")
        fs.delete(temp_dir, True)

    def get_last_checkpoint_value(
        self, table_name: str, default_value: Any = None
    ) -> Any:
        """
        Get the last checkpoint value for a table.

        Args:
            table_name: Name of the table
            default_value: Default value if no checkpoint exists

        Returns:
            Last checkpoint value or default_value
        """
        checkpoint = self.get_checkpoint(table_name)

        if checkpoint is None:
            return default_value

        return checkpoint.get("last_checkpoint", default_value)

    def initialize_checkpoint(self, table_name: str, load_type: str) -> Any:
        """
        Initialize checkpoint for a table if it doesn't exist.

        Args:
            table_name: Name of the table
            load_type: Loading strategy ('full', 'id_incremental', 'date_incremental')

        Returns:
            Initial checkpoint value (0 for ID, '1970-01-01 00:00:00' for date)
        """
        existing = self.get_checkpoint(table_name)

        if existing is not None:
            return existing.get("last_checkpoint")

        # Set default based on load type
        if load_type == "id_incremental":
            return 0
        elif load_type == "date_incremental":
            return "1970-01-01 00:00:00"
        else:
            return None
