#!/bin/bash

# Release flow: commit + tag + push. GitHub Actions handles the Docker build
# and Docker Hub publish from the v* tag — see .github/workflows/docker-build.yml.

set -e

# Read version
VERSION=$(cat version.txt)
if [ -z "$VERSION" ]; then
    echo "Error: version.txt is empty or missing."
    exit 1
fi

# Guard: refuse if this version was already tagged.
# Catches "forgot to bump version.txt before running ./push-release.sh".
if git rev-parse --verify --quiet "refs/tags/$VERSION" >/dev/null; then
    echo "Error: tag $VERSION already exists locally. Bump version.txt before releasing."
    exit 1
fi
if git ls-remote --exit-code --tags origin "refs/tags/$VERSION" >/dev/null 2>&1; then
    echo "Error: tag $VERSION already exists on origin. Bump version.txt before releasing."
    exit 1
fi

echo "Releasing version: $VERSION"
echo "Confirm? (y/n)"
read confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted."
    exit 1
fi

echo "--- GIT STEPS ---"
echo "Staging changes..."
git add .

echo "Committing release $VERSION..."
git commit -m "Release $VERSION"

echo "Tagging $VERSION..."
git tag -a "$VERSION" -m "Release $VERSION"

echo "Pushing branch + tag..."
git push --follow-tags

echo "--------------------------------------------------"
echo "Pushed $VERSION to Git."
echo "CI will build and publish to Docker Hub automatically."
echo "Watch the run: gh run watch --workflow=docker-build.yml"
echo "--------------------------------------------------"
