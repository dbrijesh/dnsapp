# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (lightweight - no ODBC for SQLite)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-azure.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-azure.txt

# Copy project
COPY . /app/

# Create directories for static, media files, and SQLite database
RUN mkdir -p /app/staticfiles /app/media /app/data

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create migrations and run them
RUN python manage.py makemigrations accounts programs || true
RUN python manage.py migrate || true

# Expose port
EXPOSE 8000

# Run server (migrations run on startup in case database doesn't exist)
CMD python manage.py migrate && \
    python manage.py create_sample_data && \
    gunicorn leadup.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120 --log-level info
