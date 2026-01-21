"""
Spark session factory for AWS-based execution.

Creates optimized Spark sessions with S3 configurations and production-safe defaults.
"""

import os
from pyspark.sql import SparkSession
from typing import Optional


def create_spark_session(
    app_name: str = "RetailDB-ETL",
    master: Optional[str] = None,
    enable_hive: bool = False,
) -> SparkSession:
    """
    Create and configure Spark session for AWS S3-based ETL.

    Optimized for:
    - Spark 3.x
    - AWS S3 access via s3a protocol
    - Production-safe defaults
    - No hardcoded credentials (uses IAM roles or environment variables)

    Args:
        app_name: Application name for Spark UI
        master: Spark master URL (None for auto-detect, "local[*]" for local)
        enable_hive: Whether to enable Hive support

    Returns:
        Configured SparkSession instance

    Example:
        >>> spark = create_spark_session("MyETL")
        >>> df = spark.read.parquet("s3a://bucket/path/")
    """
    builder = SparkSession.builder.appName(app_name)

    # Set master if provided
    if master:
        builder = builder.master(master)

    # MySQL JDBC Driver and Hadoop AWS (automatically downloaded via Maven)
    # Using Hadoop AWS 3.4.0 for Spark 4.1.0 compatibility
    builder = builder.config(
        "spark.jars.packages",
        "com.mysql:mysql-connector-j:8.0.33,"
        "org.apache.hadoop:hadoop-aws:3.4.0,"
        "com.amazonaws:aws-java-sdk-bundle:1.12.367",
    )

    # AWS S3 Configuration
    # Uses s3a (S3A connector) for better performance
    builder = builder.config(
        "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
    )

    # S3A Fast Upload
    builder = builder.config("spark.hadoop.fs.s3a.fast.upload", "true")

    # Connection pooling for S3
    builder = builder.config("spark.hadoop.fs.s3a.connection.maximum", "100")

    # AWS credentials provider (uses environment variables or IAM role)
    builder = builder.config(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    )

    # Pass AWS credentials from environment
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    if aws_access_key and aws_secret_key:
        builder = builder.config("spark.hadoop.fs.s3a.access.key", aws_access_key)
        builder = builder.config("spark.hadoop.fs.s3a.secret.key", aws_secret_key)

    # Performance optimizations
    builder = builder.config("spark.sql.adaptive.enabled", "true")
    builder = builder.config("spark.sql.adaptive.coalescePartitions.enabled", "true")

    # Parquet optimizations
    builder = builder.config("spark.sql.parquet.compression.codec", "snappy")
    builder = builder.config("spark.sql.parquet.mergeSchema", "false")
    builder = builder.config("spark.sql.parquet.filterPushdown", "true")

    # Memory and shuffle settings
    builder = builder.config("spark.sql.shuffle.partitions", "200")
    builder = builder.config("spark.sql.files.maxPartitionBytes", "134217728")  # 128MB

    # Enable Hive support if requested
    if enable_hive:
        builder = builder.enableHiveSupport()

    # Create session
    spark = builder.getOrCreate()

    # Set log level to reduce noise
    spark.sparkContext.setLogLevel("WARN")

    return spark


def stop_spark_session(spark: SparkSession):
    """
    Gracefully stop Spark session.

    Args:
        spark: SparkSession to stop
    """
    if spark:
        spark.stop()
