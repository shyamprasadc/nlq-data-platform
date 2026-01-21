# Retail DB ETL Pipeline

Production-grade PySpark ETL for ingesting retail database tables from MySQL to S3 with support for multiple loading strategies.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         ETL Pipeline                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│   │  MySQL   │───▶│  Reader  │───▶│ Validate │───▶│  Writer  │ │
│   │ retail_db│    │          │    │          │    │    S3    │ │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│                                                         │       │
│                                                         ▼       │
│                                                  ┌──────────┐   │
│                                                  │Checkpoint│   │
│                                                  │   (S3)   │   │
│                                                  └──────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Supported Load Strategies

| Strategy | Tables | Description |
|----------|--------|-------------|
| **Full Refresh** | categories, departments | Loads entire table, overwrites existing data |
| **ID Incremental** | customers, products, order_items | Loads rows where `id > last_max_id` |
| **Date Incremental** | orders | Loads rows where `order_date > last_timestamp` |

## How Incremental Loading Works

### ID-Based Incremental (customers, products, order_items)
1. Read last processed ID from checkpoint
2. Query: `SELECT * FROM table WHERE id > last_max_id`
3. Write new rows to S3 (append mode)
4. Save new max ID to checkpoint

### Date-Based Incremental (orders)
1. Read last processed date from checkpoint
2. Query: `SELECT * FROM orders WHERE order_date > last_timestamp`
3. Write new rows to S3 (partitioned by year/month/day)
4. Save new max date to checkpoint

### Full Refresh (categories, departments)
1. Query: `SELECT * FROM table`
2. Write to S3 (overwrite mode)
3. Partition by `load_date`

## Project Structure

```
etl/
├── main.py                # Main entrypoint/orchestrator
├── config/
│   └── tables.yaml        # Table metadata configuration
├── spark/
│   └── session.py         # Spark session factory
├── readers/
│   └── mysql_reader.py    # MySQL JDBC reader
├── writers/
│   └── s3_writer.py       # S3 Parquet writer
├── checkpoint/
│   └── manager.py         # Checkpoint state management
├── validation/
│   └── validators.py      # Data quality checks
├── utils/
│   └── logger.py          # Logging utilities
└── README.md              # This file
```

## Required Environment Variables

```bash
# MySQL Connection
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_DATABASE=retail_db
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password

# S3 Configuration
export S3_BUCKET=your-data-lake-bucket
export S3_PREFIX=raw/retail_db
export S3_CHECKPOINT_PREFIX=checkpoints/retail_db

# AWS Credentials (if not using IAM roles)
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

## Running the Pipeline

### Local Development

```bash
# Install dependencies
pip install pyspark pyyaml

# Set environment variables
source .env  # or export individually

# Run ETL
cd /path/to/nlq-data-platform
python -m etl.main
```

### On AWS EMR

```bash
# Submit as Spark application
spark-submit \
  --master yarn \
  --deploy-mode cluster \
  --packages mysql:mysql-connector-java:8.0.30 \
  --py-files etl.zip \
  etl/main.py
```

### On Databricks

1. Upload `etl/` directory to Databricks workspace
2. Create a job with:
   - Cluster: Any Spark 3.x cluster with MySQL driver
   - Task: Python script `etl/main.py`
   - Environment variables: Set in cluster config

## Data Validation

The pipeline validates:
- ✅ Primary key not null
- ✅ No duplicate primary keys
- ✅ Row count > 0 (for incremental loads, 0 is allowed)
- ✅ orders.order_date not null

Pipeline fails immediately if validation fails.

## Output Format

Data is written to S3 in **Parquet** format:

```
s3://bucket/raw/retail_db/
├── orders/
│   ├── year=2024/month=1/day=15/
│   │   └── part-00000.parquet
│   └── year=2024/month=1/day=16/
│       └── part-00000.parquet
├── customers/
│   ├── load_date=2024-01-15/
│   │   └── part-00000.parquet
│   └── load_date=2024-01-16/
│       └── part-00000.parquet
└── categories/
    └── load_date=2024-01-16/
        └── part-00000.parquet
```

## Checkpoints

Stored in S3 as JSON:

```
s3://bucket/checkpoints/retail_db/
├── customers.json
├── orders.json
└── products.json
```

Example checkpoint:
```json
{
  "table_name": "orders",
  "last_checkpoint": "2024-01-15 23:59:59",
  "last_updated": "2024-01-16T10:30:00+05:30",
  "row_count": 1500
}
```
