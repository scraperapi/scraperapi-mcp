FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md poetry.lock /app/
COPY src/ /app/src/

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# The API_KEY will be provided at runtime with docker run -e

CMD ["python", "-m", "scraperapi_mcp_server"]