FROM python:3.10-alpine AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk update && \
        apk add python3-dev && \
        adduser -DS python && \
        addgroup python && \
        mkdir -p /web && \
        chown python:python /web

WORKDIR /web

USER python

ENV PATH=$PATH:/home/python/.local/bin

RUN python3 -m pip install --upgrade pip

COPY --chown=python:python requirements.txt .

RUN python3 -m pip install -r requirements.txt

EXPOSE 5000

FROM base AS prod

COPY --chown=python:python . .

ENTRYPOINT ["python3", "-m", "gunicorn", "main:create_app()", "--workers", "4", "--bind", "0.0.0.0:5000"]
