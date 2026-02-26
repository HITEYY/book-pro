# syntax=docker/dockerfile:1.7

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    BOOK_PRO_OUTPUT_DIR=/app/books

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY app ./app
COPY web ./web
COPY README.md SKILL.md .env.example ./

RUN mkdir -p /app/books \
    && adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
VOLUME ["/app/books"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
