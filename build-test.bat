@echo off
setlocal enabledelayedexpansion

if "%DOCKER_USERNAME%"=="" (
    echo Error: DOCKER_USERNAME environment variable is not set
    echo Usage: set DOCKER_USERNAME=yourusername ^& build-test.bat
    exit /b 1
)

REM Always use 'test' tag for development
echo Building Docker image with test tag...
docker build -t %DOCKER_USERNAME%/deletarr:test .

REM Push test tag to Docker Hub
echo Pushing test tag to Docker Hub...
docker push %DOCKER_USERNAME%/deletarr:test

echo Successfully built and pushed test version
echo.
echo To use in TrueNAS Scale, update your app to use: %DOCKER_USERNAME%/deletarr:test
pause