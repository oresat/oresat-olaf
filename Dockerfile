FROM python:3.9-slim-bullseye

COPY requirements-dev.txt /

RUN pip install -r requirements-dev.txt
