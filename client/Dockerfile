FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY run.py /app/run.py
COPY fixtures /app/fixtures

CMD ["python", "/app/run.py"]
