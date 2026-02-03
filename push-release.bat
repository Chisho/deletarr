@echo off
setlocal enabledelayedexpansion

if "%DOCKER_USERNAME%"=="" (
    echo Error: DOCKER_USERNAME environment variable is not set
    echo Usage: set DOCKER_USERNAME=yourusername ^& push-release.bat
    exit /b 1
)

set /p VERSION=<version.txt
if "%VERSION%"=="" (
    echo Error: version.txt is empty or missing.
    exit /b 1
)

echo Deploying version: %VERSION%
set /p confirm="Confirm? (y/n): "
if not "%confirm%"=="y" (
    echo Aborted.
    exit /b 1
)

echo --- GIT STEPS ---
echo Staging changes...
git add .

echo Commiting version change...
git commit -m "Release %VERSION%"

echo Tagging version %VERSION%...
git tag -a "%VERSION%" -m "Release %VERSION%"

echo Pushing to Git...
git push
git push origin "%VERSION%"

echo --- DOCKER STEPS ---
echo Building Docker image version %VERSION%...
docker build -t %DOCKER_USERNAME%/deletarr:%VERSION% -t %DOCKER_USERNAME%/deletarr:latest .

echo Pushing versions to Docker Hub...
docker push %DOCKER_USERNAME%/deletarr:%VERSION%
docker push %DOCKER_USERNAME%/deletarr:latest

echo --------------------------------------------------
echo Successfully released version %VERSION% to Git and Docker
echo --------------------------------------------------
pause
