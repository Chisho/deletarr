# Start from your base image (e.g., python:3.10-slim)
FROM python:3.10-slim

LABEL version="0.0.1"
LABEL description="Automatically clean up torrents from qBittorrent that are no longer in Radarr/Sonarr"
LABEL maintainer="Your Name <your.email@example.com>"

WORKDIR /app

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy version file
COPY version.txt /app/version.txt

# Copy requirements if present
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy package folder
COPY deletarr /app/deletarr

# Copy sample config (not used at runtime)
COPY config_sample /config_sample

# Do not copy config/config.yml; user must mount /config

# Copy entrypoint script and fix line endings
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Set up deletarr shell command
RUN echo '#!/bin/sh\nexec python -m deletarr.main "$@"' > /usr/local/bin/deletarr && chmod +x /usr/local/bin/deletarr

ENTRYPOINT ["/entrypoint.sh"]