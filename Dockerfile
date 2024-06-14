FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

COPY . /app/

CMD ["poetry", "run", "uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000"]
