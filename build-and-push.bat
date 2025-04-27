@echo off
setlocal enabledelayedexpansion

REM Read version from version.txt
set /p VERSION=<version.txt

if "%DOCKER_USERNAME%"=="" (
    echo Error: DOCKER_USERNAME environment variable is not set
    echo Usage: set DOCKER_USERNAME=yourusername ^& build-and-push.bat
    exit /b 1
)

REM Build the image with version tag and latest
echo Building Docker image version %VERSION%...
docker build -t %DOCKER_USERNAME%/deletarr:%VERSION% -t %DOCKER_USERNAME%/deletarr:latest .

REM Push both tags to Docker Hub
echo Pushing version %VERSION% to Docker Hub...
docker push %DOCKER_USERNAME%/deletarr:%VERSION%
docker push %DOCKER_USERNAME%/deletarr:latest

echo Successfully built and pushed version %VERSION%