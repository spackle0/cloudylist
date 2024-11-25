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
    && poetry install --no-interaction # --no-ansi # maybe colors in github actions output

# Copy application code
COPY cloudylist ./cloudylist

##########
# Testing image with development dependencies
##########
FROM base AS testing

# Add tests to the image
COPY tests ./tests

# Install additional development dependencies
RUN poetry install --with dev --no-interaction

# Entry point for running tests
ENTRYPOINT ["poetry", "run", "pytest"]

##########
# Production image, lean
##########
FROM base AS production

# Default entry point for production
ENTRYPOINT ["poetry", "run", "cloudylist"]
