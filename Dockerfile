FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV UV_PROJECT_ENVIRONMENT=/opt/venv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY schemas schemas
COPY tantar.toml tantar.toml
COPY tantar tantar
COPY alembic.ini alembic.ini
COPY alembic alembic
COPY scheduler.py scheduler.py
COPY process_file.py process_file.py

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "tantar.app:app", "--host", "0.0.0.0", "--port", "8000"]
