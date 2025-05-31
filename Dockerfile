# Use official Python image as base
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        gcc \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port (Flask default)
EXPOSE 5050

# Set environment variables (can be overridden at runtime)
ENV PYTHONUNBUFFERED=1

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "2", "--worker-class", "gthread", "--threads", "2", "--worker-connections", "50", "--timeout", "300", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
