# Use slim python image
FROM mycountregistry.azurecr.io/python:3.11-slim AS base

# Set workdir
WORKDIR /app

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