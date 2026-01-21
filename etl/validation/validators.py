"""
Data validation and quality checks for ETL pipeline.

Ensures data integrity before writing to data lake.
"""

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, count, when, isnan, isnull
from typing import List, Tuple


class DataValidator:
    """
    Data quality validator for ETL pipeline.

    Performs validation checks:
    - Primary key not null
    - No duplicate primary keys
    - Row count validation
    - Table-specific validations
    """

    def __init__(self, df: DataFrame, table_name: str):
        """
        Initialize validator.

        Args:
            df: DataFrame to validate
            table_name: Name of the table being validated
        """
        self.df = df
        self.table_name = table_name
        self.errors = []

    def validate_primary_key_not_null(self, primary_key: str) -> bool:
        """
        Validate that primary key column has no null values.

        Args:
            primary_key: Name of the primary key column

        Returns:
            True if validation passes, False otherwise
        """
        null_count = self.df.filter(col(primary_key).isNull()).count()

        if null_count > 0:
            self.errors.append(
                f"Primary key '{primary_key}' has {null_count} null values"
            )
            return False

        return True

    def validate_no_duplicates(self, primary_key: str) -> bool:
        """
        Validate that primary key has no duplicate values.

        Args:
            primary_key: Name of the primary key column

        Returns:
            True if validation passes, False otherwise
        """
        total_count = self.df.count()
        distinct_count = self.df.select(primary_key).distinct().count()

        if total_count != distinct_count:
            duplicate_count = total_count - distinct_count
            self.errors.append(
                f"Primary key '{primary_key}' has {duplicate_count} duplicate values"
            )
            return False

        return True

    def validate_row_count(
        self, min_rows: int = 1, is_incremental: bool = False
    ) -> bool:
        """
        Validate that DataFrame has minimum number of rows.

        Args:
            min_rows: Minimum expected row count
            is_incremental: If True, allows 0 rows (no new data)

        Returns:
            True if validation passes, False otherwise
        """
        row_count = self.df.count()

        # For incremental loads, 0 rows is acceptable (no new data)
        if is_incremental and row_count == 0:
            return True

        if row_count < min_rows:
            self.errors.append(
                f"Row count ({row_count}) is less than minimum ({min_rows})"
            )
            return False

        return True

    def validate_column_not_null(self, column_name: str) -> bool:
        """
        Validate that a specific column has no null values.

        Args:
            column_name: Name of the column to validate

        Returns:
            True if validation passes, False otherwise
        """
        if column_name not in self.df.columns:
            self.errors.append(f"Column '{column_name}' does not exist in DataFrame")
            return False

        null_count = self.df.filter(col(column_name).isNull()).count()

        if null_count > 0:
            self.errors.append(f"Column '{column_name}' has {null_count} null values")
            return False

        return True

    def validate_orders_table(self, primary_key: str) -> bool:
        """
        Specific validation for orders table.

        Args:
            primary_key: Name of the primary key column

        Returns:
            True if all validations pass, False otherwise
        """
        validations = [
            self.validate_primary_key_not_null(primary_key),
            self.validate_no_duplicates(primary_key),
            self.validate_column_not_null("order_date"),  # order_date must not be null
        ]

        return all(validations)

    def validate_all(
        self, primary_key: str, load_type: str = "full"
    ) -> Tuple[bool, List[str]]:
        """
        Run all standard validations.

        Args:
            primary_key: Name of the primary key column
            load_type: Loading strategy ('full', 'id_incremental', 'date_incremental')

        Returns:
            Tuple of (validation_passed, list_of_errors)
        """
        is_incremental = load_type in ["id_incremental", "date_incremental"]

        # Standard validations
        validations = [
            self.validate_primary_key_not_null(primary_key),
            self.validate_no_duplicates(primary_key),
            self.validate_row_count(min_rows=1, is_incremental=is_incremental),
        ]

        # Table-specific validations
        if self.table_name == "orders":
            validations.append(self.validate_column_not_null("order_date"))

        all_passed = all(validations)

        return all_passed, self.errors

    def get_validation_summary(self) -> str:
        """
        Get summary of validation results.

        Returns:
            Human-readable validation summary
        """
        if not self.errors:
            return f"✓ All validations passed for {self.table_name}"

        error_summary = "\n".join([f"  - {error}" for error in self.errors])
        return f"✗ Validation failed for {self.table_name}:\n{error_summary}"
