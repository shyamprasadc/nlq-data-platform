#!/usr/bin/env python3
"""
Main ETL orchestrator for Retail Database ingestion.

This is the entrypoint for the ETL pipeline that:
1. Loads table configuration
2. Initializes Spark session
3. Processes each table based on its load strategy
4. Validates data quality
5. Writes to S3
6. Updates checkpoints

Usage:
    python -m etl.main

Environment Variables:
    MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
    S3_BUCKET, S3_PREFIX, S3_CHECKPOINT_PREFIX
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Load environment variables from .env file
from dotenv import load_dotenv

# Try loading .env from etl directory first, then project root
etl_env = Path(__file__).parent / ".env"
root_env = Path(__file__).parent.parent / ".env"

if etl_env.exists():
    load_dotenv(etl_env)
elif root_env.exists():
    load_dotenv(root_env)

from etl.spark.session import create_spark_session, stop_spark_session  # noqa: E402
from etl.readers.mysql_reader import MySQLReader  # noqa: E402
from etl.writers.s3_writer import S3Writer  # noqa: E402
from etl.checkpoint.manager import CheckpointManager  # noqa: E402
from etl.validation.validators import DataValidator  # noqa: E402
from etl.utils.logger import setup_logger, TableLogger  # noqa: E402


def load_table_config() -> List[Dict[str, Any]]:
    """
    Load table configuration from YAML file.

    Returns:
        List of table configuration dictionaries
    """
    config_path = Path(__file__).parent / "config" / "tables.yaml"

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config.get("tables", [])


def get_environment_config() -> Dict[str, str]:
    """
    Get required environment variables.

    Returns:
        Dictionary of environment configuration

    Raises:
        ValueError: If required environment variables are missing
    """
    required_vars = [
        "MYSQL_HOST",
        "MYSQL_DATABASE",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "S3_BUCKET",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return {
        "mysql_host": os.getenv("MYSQL_HOST"),
        "mysql_port": os.getenv("MYSQL_PORT", "3306"),
        "mysql_database": os.getenv("MYSQL_DATABASE"),
        "mysql_user": os.getenv("MYSQL_USER"),
        "mysql_password": os.getenv("MYSQL_PASSWORD"),
        "s3_bucket": os.getenv("S3_BUCKET"),
        "s3_prefix": os.getenv("S3_PREFIX", "raw/retail_db"),
        "s3_checkpoint_prefix": os.getenv(
            "S3_CHECKPOINT_PREFIX", "checkpoints/retail_db"
        ),
    }


def process_table(
    table_config: Dict[str, Any],
    reader: MySQLReader,
    writer: S3Writer,
    checkpoint_manager: CheckpointManager,
    table_logger: TableLogger,
) -> bool:
    """
    Process a single table through the ETL pipeline.

    Args:
        table_config: Table configuration dictionary
        reader: MySQL reader instance
        writer: S3 writer instance
        checkpoint_manager: Checkpoint manager instance
        table_logger: Logger for this table

    Returns:
        True if processing succeeded, False otherwise
    """
    table_name = table_config["table_name"]
    load_type = table_config["load_type"]
    primary_key = table_config["primary_key"]
    incremental_column = table_config.get("incremental_column")
    partition_strategy = table_config["partition_strategy"]

    try:
        table_logger.start()

        # Step 1: Get checkpoint for incremental loads
        last_checkpoint = None
        if load_type in ["id_incremental", "date_incremental"]:
            last_checkpoint = checkpoint_manager.initialize_checkpoint(
                table_name, load_type
            )
            table_logger.info(f"Checkpoint: {last_checkpoint}")

        # Step 2: Read data from MySQL
        table_logger.info(f"Reading data (strategy: {load_type})")
        df = reader.read_with_strategy(
            table_name=table_name,
            load_type=load_type,
            incremental_column=incremental_column,
            last_checkpoint=last_checkpoint,
        )

        row_count = df.count()
        table_logger.info(f"Read {row_count:,} rows from MySQL")

        # Step 3: Handle no data for incremental loads
        if row_count == 0:
            if load_type in ["id_incremental", "date_incremental"]:
                table_logger.info("No new data to process")
                table_logger.success(0)
                return True
            else:
                table_logger.warning("No data found for full refresh")

        # Step 4: Validate data quality
        table_logger.info("Validating data quality")
        validator = DataValidator(df, table_name)
        is_valid, errors = validator.validate_all(primary_key, load_type)

        if not is_valid:
            for error in errors:
                table_logger.error(f"Validation failed: {error}")
            raise ValueError(f"Data validation failed: {errors}")

        table_logger.info("Data validation passed")

        # Step 5: Write to S3
        table_logger.info(f"Writing to S3 (partition: {partition_strategy})")
        writer.write_with_strategy(
            df=df,
            table_name=table_name,
            partition_strategy=partition_strategy,
            date_column=incremental_column if partition_strategy == "date" else None,
            load_type=load_type,
        )

        # Step 6: Update checkpoint
        if load_type == "id_incremental":
            new_checkpoint = df.agg({primary_key: "max"}).collect()[0][0]
            checkpoint_manager.save_checkpoint(table_name, new_checkpoint, row_count)
            table_logger.info(f"Updated checkpoint to {new_checkpoint}")

        elif load_type == "date_incremental":
            new_checkpoint = df.agg({incremental_column: "max"}).collect()[0][0]
            # Convert datetime to string for storage
            new_checkpoint_str = str(new_checkpoint)
            checkpoint_manager.save_checkpoint(
                table_name, new_checkpoint_str, row_count
            )
            table_logger.info(f"Updated checkpoint to {new_checkpoint_str}")

        table_logger.success(row_count)
        return True

    except Exception as e:
        table_logger.failure(e)
        return False


def run_etl():
    """
    Main ETL execution function.

    Orchestrates the entire ETL pipeline:
    - Loads configuration
    - Initializes components
    - Processes each table
    - Reports results
    """
    logger = setup_logger("etl")
    logger.info("=" * 60)
    logger.info("Starting Retail DB ETL Pipeline")
    logger.info("=" * 60)

    spark = None

    try:
        # Load configuration
        env_config = get_environment_config()
        table_configs = load_table_config()

        logger.info(f"Loaded configuration for {len(table_configs)} tables")

        # Initialize Spark session
        logger.info("Initializing Spark session")
        spark = create_spark_session("RetailDB-ETL", master="local[*]")
        logger.info(f"Spark version: {spark.version}")

        # Initialize components
        reader = MySQLReader(spark)
        writer = S3Writer(
            s3_bucket=env_config["s3_bucket"], s3_prefix=env_config["s3_prefix"]
        )
        checkpoint_manager = CheckpointManager(
            spark=spark,
            s3_checkpoint_path=f"s3a://{env_config['s3_bucket']}/{env_config['s3_checkpoint_prefix']}",
        )

        # Process each table
        results = {}
        for table_config in table_configs:
            table_name = table_config["table_name"]
            table_logger = TableLogger(table_name, logger)

            success = process_table(
                table_config=table_config,
                reader=reader,
                writer=writer,
                checkpoint_manager=checkpoint_manager,
                table_logger=table_logger,
            )

            results[table_name] = "SUCCESS" if success else "FAILED"

        # Summary report
        logger.info("=" * 60)
        logger.info("ETL Pipeline Summary")
        logger.info("=" * 60)

        success_count = sum(1 for r in results.values() if r == "SUCCESS")
        failed_count = sum(1 for r in results.values() if r == "FAILED")

        for table, status in results.items():
            status_icon = "✓" if status == "SUCCESS" else "✗"
            logger.info(f"  {status_icon} {table}: {status}")

        logger.info("-" * 60)
        logger.info(f"Total: {success_count} succeeded, {failed_count} failed")

        # Exit with error if any table failed
        if failed_count > 0:
            logger.error("ETL completed with errors")
            sys.exit(1)
        else:
            logger.info("ETL completed successfully")

    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}")
        raise

    finally:
        if spark:
            logger.info("Stopping Spark session")
            stop_spark_session(spark)


if __name__ == "__main__":
    run_etl()
