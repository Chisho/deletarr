#!/bin/bash

# Configuration
if [ -z "$DOCKER_USERNAME" ]; then
    echo "Error: DOCKER_USERNAME environment variable is not set"
    echo "Usage: DOCKER_USERNAME=yourusername ./push-dev.sh"
    exit 1
fi

# Generate a unique dev tag based on timestamp
DEV_TAG="dev-$(date +%Y%m%d-%H%M%S)"

echo "--- GIT STEPS ---"
echo "Staging changes..."
git add .

echo "Commiting changes with message: Dev push: $DEV_TAG"
git commit -m "Dev push: $DEV_TAG"

echo "Pushing to Git..."
git push

echo "--- DOCKER STEPS ---"
# Try to find docker if not in PATH
DOCKER_BIN=$(which docker)
if [ -z "$DOCKER_BIN" ] && [ -f "/Applications/Docker.app/Contents/Resources/bin/docker" ]; then
    DOCKER_BIN="/Applications/Docker.app/Contents/Resources/bin/docker"
fi

if [ -z "$DOCKER_BIN" ]; then
    echo "Error: docker command not found. Please ensure Docker is installed and in your PATH."
    exit 1
fi

echo "Building Docker image with dev tag: $DEV_TAG for platform linux/amd64..."
"$DOCKER_BIN" build --platform linux/amd64 -t "$DOCKER_USERNAME/deletarr:$DEV_TAG" .

echo "Pushing dev tag $DEV_TAG to Docker Hub..."
"$DOCKER_BIN" push "$DOCKER_USERNAME/deletarr:$DEV_TAG"

echo "--------------------------------------------------"
echo "Successfully pushed to Git and Docker (Tag: $DEV_TAG)"
echo "--------------------------------------------------"
