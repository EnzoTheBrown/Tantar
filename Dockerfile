FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml pyproject.toml
RUN uv lock
RUN uv sync --frozen

COPY schemas schemas
COPY tantar.toml tantar.toml
COPY tantar tantar
COPY alembic.ini alembic.ini
COPY alembic alembic
COPY scheduler.py scheduler.py
COPY process_file.py process_file.py
