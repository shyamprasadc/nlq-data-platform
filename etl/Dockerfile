# PySpark ETL Pipeline Docker Image

# Use official Spark image with Python support
FROM apache/spark-py:v3.5.0

# Set working directory
WORKDIR /app

# Switch to root to install dependencies
USER root

# Install Python dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./
RUN uv pip install --system --no-cache pyyaml python-dotenv

# Copy ETL code
COPY etl/ ./etl/

# Environment variables
ENV PYTHONPATH=/app
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Switch back to non-root spark user
USER 185

# Default command runs the ETL pipeline
CMD ["python", "-m", "etl.main"]
