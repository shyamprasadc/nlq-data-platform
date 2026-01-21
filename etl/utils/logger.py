"""
Logging utilities for ETL pipeline.

Provides structured logging with per-table tracking and success/failure reporting.
"""

import logging
import sys
from datetime import datetime
from typing import Optional


def setup_logger(name: str = "etl", level: int = logging.INFO) -> logging.Logger:
    """
    Set up structured logger for ETL pipeline.

    Args:
        name: Logger name
        level: Logging level

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with formatting
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger


class TableLogger:
    """Context-aware logger for table-specific operations."""

    def __init__(self, table_name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize table logger.

        Args:
            table_name: Name of the table being processed
            logger: Parent logger instance (creates new if None)
        """
        self.table_name = table_name
        self.logger = logger or setup_logger()
        self.start_time = None

    def start(self):
        """Mark start of table processing."""
        self.start_time = datetime.now()
        self.logger.info(f"[{self.table_name}] Starting ETL processing")

    def info(self, message: str):
        """Log info message for table."""
        self.logger.info(f"[{self.table_name}] {message}")

    def warning(self, message: str):
        """Log warning message for table."""
        self.logger.warning(f"[{self.table_name}] {message}")

    def error(self, message: str):
        """Log error message for table."""
        self.logger.error(f"[{self.table_name}] {message}")

    def success(self, row_count: int):
        """Log successful completion with metrics."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.logger.info(
                f"[{self.table_name}] ✓ SUCCESS - Processed {row_count:,} rows in {duration:.2f}s"
            )
        else:
            self.logger.info(
                f"[{self.table_name}] ✓ SUCCESS - Processed {row_count:,} rows"
            )

    def failure(self, error: Exception):
        """Log failure with error details."""
        if self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
            self.logger.error(
                f"[{self.table_name}] ✗ FAILED after {duration:.2f}s - {str(error)}"
            )
        else:
            self.logger.error(f"[{self.table_name}] ✗ FAILED - {str(error)}")
