FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for psycopg and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency definition and lockfile
COPY pyproject.toml uv.lock ./

# Install python dependencies into global environment
RUN uv pip install --system -r pyproject.toml

# Copy backend application code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
