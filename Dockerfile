FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Project code, configs, data and model artifacts
COPY src/ ./src/
COPY apps/ ./apps/
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY docs/ ./docs/
COPY data/raw/ ./data/raw/
COPY models/ ./models/
COPY Makefile ./

EXPOSE 8000 8501 8502
