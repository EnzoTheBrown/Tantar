FROM python:3.11-slim

WORKDIR /app
COPY . /app/
RUN python -r requirements.txt

CMD ["uvicorn", "serve:app", "--host", "0.0.0.0", "--port", "8000"]
