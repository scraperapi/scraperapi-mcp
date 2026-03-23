FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock /app/

RUN poetry install --only main --no-root --no-directory

COPY README.md LICENSE /app/
COPY src/ /app/src/

RUN poetry install --only main

# The API_KEY will be provided at runtime with docker run -e

CMD ["python", "-m", "scraperapi_mcp_server"]
