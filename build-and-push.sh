#!/bin/bash

# Configuration
if [ -z "$DOCKER_USERNAME" ]; then
    echo "Error: DOCKER_USERNAME environment variable is not set"
    echo "Usage: DOCKER_USERNAME=yourusername ./build-and-push.sh"
    exit 1
fi

# Read version from version.txt
VERSION=$(cat version.txt)

# Try to find docker if not in PATH
DOCKER_BIN=$(which docker)
if [ -z "$DOCKER_BIN" ] && [ -f "/Applications/Docker.app/Contents/Resources/bin/docker" ]; then
    DOCKER_BIN="/Applications/Docker.app/Contents/Resources/bin/docker"
fi

if [ -z "$DOCKER_BIN" ]; then
    echo "Error: docker command not found. Please ensure Docker is installed and in your PATH."
    exit 1
fi

# Build the image with version tag and latest for platform linux/amd64
echo "Building Docker image version $VERSION for platform linux/amd64..."
"$DOCKER_BIN" build --platform linux/amd64 -t $DOCKER_USERNAME/deletarr:$VERSION -t $DOCKER_USERNAME/deletarr:latest .

# Push both tags to Docker Hub
echo "Pushing version $VERSION to Docker Hub..."
"$DOCKER_BIN" push $DOCKER_USERNAME/deletarr:$VERSION
"$DOCKER_BIN" push $DOCKER_USERNAME/deletarr:latest

echo "Successfully built and pushed version $VERSION"