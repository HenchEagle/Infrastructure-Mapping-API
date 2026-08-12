FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHCE_DIR=1

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup appuser

COPY --chown=appuser:appgroup . .

USER appuser

EXPOSE 8000