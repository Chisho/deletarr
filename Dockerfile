# Start from your base image (e.g., python:3.10-slim)
FROM python:3.10-slim

WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy requirements if present
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt || true

# Copy main script
COPY deletarr.py /app/deletarr.py

# Copy sample config (not used at runtime)
COPY config_sample /config_sample

# Do not copy config/config.yml; user must mount /config

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set up deletarr shell command
RUN echo '#!/bin/sh\nexec python /app/deletarr.py "$@"' > /usr/local/bin/deletarr && chmod +x /usr/local/bin/deletarr

ENTRYPOINT ["/entrypoint.sh"]