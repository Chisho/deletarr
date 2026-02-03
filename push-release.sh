#!/bin/bash

# Configuration
if [ -z "$DOCKER_USERNAME" ]; then
    echo "Error: DOCKER_USERNAME environment variable is not set"
    echo "Usage: DOCKER_USERNAME=yourusername ./push-release.sh"
    exit 1
fi

# Read version
VERSION=$(cat version.txt)
if [ -z "$VERSION" ]; then
    echo "Error: version.txt is empty or missing."
    exit 1
fi

echo "Deploying version: $VERSION"
echo "Confirm? (y/n)"
read confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted."
    exit 1
fi

echo "--- GIT STEPS ---"
echo "Staging changes..."
git add .

echo "Commiting version change..."
git commit -m "Release $VERSION"

echo "Tagging version $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION"

echo "Pushing to Git..."
git push
git push origin "$VERSION"

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

echo "Building Docker image version $VERSION for platform linux/amd64..."
"$DOCKER_BIN" build --platform linux/amd64 -t "$DOCKER_USERNAME/deletarr:$VERSION" -t "$DOCKER_USERNAME/deletarr:latest" .

echo "Pushing version $VERSION and latest to Docker Hub..."
"$DOCKER_BIN" push "$DOCKER_USERNAME/deletarr:$VERSION"
"$DOCKER_BIN" push "$DOCKER_USERNAME/deletarr:latest"

echo "--------------------------------------------------"
echo "Successfully released version $VERSION to Git and Docker"
echo "--------------------------------------------------"
