FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ../requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app/web/
COPY ../plex_cleanup.py /app/
COPY ../storage_analyzer.py /app/
COPY ../disk_utils.py /app/

# Set working directory to web
WORKDIR /app/web

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/stats || exit 1

# Run the application
CMD ["python3", "app.py"]
