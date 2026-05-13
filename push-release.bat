@echo off
setlocal enabledelayedexpansion

REM Release flow: commit + tag + push. GitHub Actions handles the Docker build
REM and Docker Hub publish from the v* tag - see .github\workflows\docker-build.yml.

set /p VERSION=<version.txt
if "%VERSION%"=="" (
    echo Error: version.txt is empty or missing.
    exit /b 1
)

REM Guard: refuse if this version was already tagged.
git rev-parse --verify --quiet "refs/tags/%VERSION%" >nul 2>&1
if not errorlevel 1 (
    echo Error: tag %VERSION% already exists locally. Bump version.txt before releasing.
    exit /b 1
)
git ls-remote --exit-code --tags origin "refs/tags/%VERSION%" >nul 2>&1
if not errorlevel 1 (
    echo Error: tag %VERSION% already exists on origin. Bump version.txt before releasing.
    exit /b 1
)

echo Releasing version: %VERSION%
set /p confirm="Confirm? (y/n): "
if not "%confirm%"=="y" (
    echo Aborted.
    exit /b 1
)

echo --- GIT STEPS ---
echo Staging changes...
git add .

echo Committing release %VERSION%...
git commit -m "Release %VERSION%"

echo Tagging %VERSION%...
git tag -a "%VERSION%" -m "Release %VERSION%"

echo Pushing branch + tag...
git push --follow-tags

echo --------------------------------------------------
echo Pushed %VERSION% to Git.
echo CI will build and publish to Docker Hub automatically.
echo --------------------------------------------------
pause
