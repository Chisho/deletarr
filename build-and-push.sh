#!/bin/bash

# Read version from version.txt
VERSION=$(cat version.txt)

# Check if DOCKER_USERNAME is set
if [ -z "$DOCKER_USERNAME" ]; then
    echo "Error: DOCKER_USERNAME environment variable is not set"
    echo "Usage: DOCKER_USERNAME=yourusername ./build-and-push.sh"
    exit 1
fi

# Build the image with version tag and latest
echo "Building Docker image version $VERSION..."
docker build -t $DOCKER_USERNAME/deletarr:$VERSION -t $DOCKER_USERNAME/deletarr:latest .

# Push both tags to Docker Hub
echo "Pushing version $VERSION to Docker Hub..."
docker push $DOCKER_USERNAME/deletarr:$VERSION
docker push $DOCKER_USERNAME/deletarr:latest

echo "Successfully built and pushed version $VERSION"