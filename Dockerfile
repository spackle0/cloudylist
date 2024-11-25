FROM python:3.12-slim AS base

# This is the pristine image

WORKDIR /app

RUN pip install --no-cache-dir poetry

# Copy project dependency files
COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy Application code only
COPY cloudylist ./cloudylist

##########
# Testing image with deps
##########
FROM base AS testing

COPY tests ./tests

# Install additional dev dependencies
RUN poetry install --with dev --no-interaction # --no-ansi # maybe remove no-ansi if colors show up in github actions

# Entry point for running tests
ENTRYPOINT ["poetry", "run", "pytest"]


##########
# Prod image, lean
##########
FROM base AS production

ENTRYPOINT ["poetry", "run", "cloudylist"]
