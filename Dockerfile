# syntax=docker/dockerfile:1
FROM python:3.9.0

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

RUN pip3 install --upgrade pip

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/