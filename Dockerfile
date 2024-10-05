# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

USER appuser

ENV PATH="${PATH}:/home/appuser/.local/bin/"
RUN mkdir -p /home/appuser/.cache/
RUN --mount=type=cache,target=/home/appuser/.cache/pip pip install --trusted-host pypi.python.org pipenv

RUN --mount=type=cache,target=/home/appuser/.cache/pipenv \
    --mount=type=bind,source=Pipfile,target=Pipfile \
    --mount=type=bind,source=Pipfile.lock,target=Pipfile.lock \
    pipenv install --system --deploy


COPY src ./src

WORKDIR /app/src
EXPOSE 3000