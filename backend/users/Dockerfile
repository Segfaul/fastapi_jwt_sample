# Backend Dockerfile

FROM python:3.11.6-slim

RUN mkdir -p /fastapi_jwt_sample/backend/users /fastapi_jwt_sample/backend/common
WORKDIR /fastapi_jwt_sample

COPY backend/users/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY .env .
COPY backend/__init__.py ./backend
COPY backend/common ./backend/common
COPY backend/users ./backend/users
