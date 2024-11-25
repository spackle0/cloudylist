# Base image for shared dependencies
FROM python:3.12-slim AS base

# Set environment variables for better Python behavior
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy project dependency files
COPY pyproject.toml poetry.lock ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction

# Copy application code
COPY cloudylist ./cloudylist
COPY config.yml ./

##########
# Testing image with development dependencies
##########
FROM base AS testing

# Add tests and coverage configuration
COPY tests ./tests
COPY .coveragerc ./

# Install additional development dependencies
RUN poetry install --with dev --no-interaction

# Default COVERAGE value for local testing
ENV COVERAGE=85

# Entry point for running tests with dynamic coverage thresholds
ENTRYPOINT ["sh", "-c", "poetry run pytest --cov=cloudylist --cov-report=term-missing --cov-fail-under=${COVERAGE} tests"]

##########
# Production image, lean
##########
FROM base AS production

# Default entry point for production
ENTRYPOINT ["poetry", "run", "cloudylist"]
