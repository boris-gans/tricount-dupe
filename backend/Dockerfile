# Use slim python image
FROM python:3.11-slim AS base

# Set workdir
WORKDIR /app

# Define envs
ARG DATABASE_USER
ARG DATABASE_PW
ARG DATABASE_NAME
ARG DATABASE_URL
ARG JWT_SECRET_KEY
ARG JWT_ALGORITHM
ARG JWT_EXPIRATION_MINUTES
ARG BACKEND_PORT
ARG FRONTEND_PORT
ARG LOG_FORMAT
ARG BASE_LOGGER_NAME

ENV DATABASE_USER=$DATABASE_USER
ENV DATABASE_PW=$DATABASE_PW
ENV DATABASE_NAME=$DATABASE_NAME
ENV DATABASE_URL=$DATABASE_URL
ENV JWT_SECRET_KEY=$JWT_SECRET_KEY
ENV JWT_ALGORITHM=$JWT_ALGORITHM
ENV JWT_EXPIRATION_MINUTES=$JWT_EXPIRATION_MINUTES
ENV BACKEND_PORT=$BACKEND_PORT
ENV FRONTEND_PORT=$FRONTEND_PORT
ENV LOG_FORMAT=$LOG_FORMAT
ENV BASE_LOGGER_NAME=$BASE_LOGGER_NAME

# Install system dependencies (optional, e.g. psycopg2 needs gcc & postgres headers)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]