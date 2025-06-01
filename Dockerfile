# Use Python 3.11 slim image as base
FROM python:3.11-slim-bullseye as base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and make it available in PATH
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && cd /usr/local/bin \
    && ln -s /opt/poetry/bin/poetry poetry

# Verify poetry installation
RUN poetry --version

# Set up app directory  
WORKDIR /app

# Copy only requirements files to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Development stage
FROM base as development
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Create a non-root user
RUN useradd -m app_user
USER app_user

# Copy the rest of the code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Production stage
FROM base as production
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --only main

# Create a non-root user
RUN useradd -m app_user
USER app_user

# Copy the rest of the code
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Default command
CMD ["python", "run_adk_agent.py"]