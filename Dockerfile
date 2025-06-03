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
        ghostscript \
        qpdf \
        pdftk \
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
# Optimize system limits for many concurrent connections
RUN echo "* soft nofile 65535" >> /etc/security/limits.conf && \
    echo "* hard nofile 65535" >> /etc/security/limits.conf

# Run with Gunicorn optimized for single core
CMD ["gunicorn", "--bind", "0.0.0.0:5050", \
     "--workers", "4", \
     "--worker-class", "gthread", \
     "--threads", "128", \
     "--worker-connections", "1000", \
     "--backlog", "1024", \
     "--max-requests", "10000", \
     "--max-requests-jitter", "1000", \
     "--timeout", "300", \
     "--keep-alive", "2", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:app"]