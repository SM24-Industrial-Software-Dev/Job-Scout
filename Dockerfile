# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.1
FROM python:${PYTHON_VERSION}-slim as base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip config set global.trusted-host "pypi.org files.pythonhosted.org pypi.python.org"
RUN python -m pip install -r requirements.txt

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

USER appuser

COPY . .

EXPOSE 8000

ENV AWS_ACCESS_KEY_ID=AKIAU6GDY7SDKAJZPNRI

ENV AWS_SECRET_ACCESS_KEY=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

ENV AWS_REGION=us-east-1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]