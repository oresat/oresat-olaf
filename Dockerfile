FROM python:3.9-slim-bullseye

COPY requirements.txt /

RUN pip install -r requirements.txt
