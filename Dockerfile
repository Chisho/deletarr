# --- Stage 1: Build Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
# Build the frontend to /app/frontend/dist
RUN npm run build

# --- Stage 2: Final Image ---
FROM python:3.10-slim

ARG VERSION=unknown

LABEL org.opencontainers.image.version="${VERSION}"
LABEL org.opencontainers.image.description="Automatically clean up torrents from qBittorrent that are no longer in Radarr/Sonarr"
LABEL org.opencontainers.image.source="https://github.com/Chisho/deletarr"

WORKDIR /app

# Install cron and git (git often useful for versioning)
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Copy version file
COPY version.txt /app/version.txt

# Copy requirements
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend code
COPY deletarr /app/deletarr

# Copy built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Env var to tell API where frontend is
ENV FRONTEND_DIST=/app/frontend/dist

# Copy sample config
COPY config_sample /config_sample

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

# Expose Web UI port
EXPOSE 8000

# Healthcheck — hits /api/health. Uses python (already in the image) so we don't need to install curl.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=3).read()" || exit 1

# We replace the old shell command with the entrypoint script handling
# But we should update entrypoint.sh to start uvicorn
ENTRYPOINT ["/entrypoint.sh"]