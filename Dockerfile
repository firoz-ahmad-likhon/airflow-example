# Apache Airflow image as the base
FROM apache/airflow:2.10.2

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
COPY .ruff.toml .
COPY .mypy.ini .
COPY pytest.ini .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create directories (if not created already)
RUN mkdir -p /opt/airflow/dags /opt/airflow/plugins /opt/airflow/logs

# Copy your local files to the container
COPY ./dags /opt/airflow/dags
COPY ./tests /opt/airflow/tests

# Expose the Airflow webserver port
EXPOSE 8080

# Default command (will be overridden in docker-compose for different services)
CMD ["airflow", "webserver"]
