# Apache Airflow image as the base
FROM apache/airflow:2.10.2 AS base

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow

# Switch to root user to install additional packages
USER root

# Install additional packages
RUN apt-get update && \
    apt-get install --no-install-recommends -y curl vim && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Set working directory
WORKDIR /opt/airflow

# Copy necessary files to the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories (if not created already)
RUN mkdir -p dags tests

# Copy your local files to the container
COPY ./dags .
COPY ./tests .

# Production stage
FROM base AS prod

# Expose the Airflow webserver port
EXPOSE 8080

# Default command (will be overridden in docker-compose for different services)
CMD ["airflow", "webserver"]

# Development stage
FROM base AS dev

# Install additional development packages
RUN pip install pytest==8.3.3 pytest-mock==3.14.0 mypy==1.11.2 ruff==0.6.9 types-requests==2.32.0.20240914

# Copy relevant configuration files for development
COPY .ruff.toml ./
COPY .mypy.ini ./
COPY pytest.ini ./

# Expose the Airflow webserver port
EXPOSE 8080

# Default command (will be overridden in docker-compose for different services)
CMD ["airflow", "webserver"]
