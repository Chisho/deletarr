@echo off
setlocal enabledelayedexpansion

if "%DOCKER_USERNAME%"=="" (
    echo Error: DOCKER_USERNAME environment variable is not set
    echo Usage: set DOCKER_USERNAME=yourusername ^& build-dev.bat
    exit /b 1
)

REM Use current timestamp for unique dev tag
for /f "tokens=1-4 delims=/ " %%i in ('date /t') do set mydate=%%i-%%j-%%k
for /f "tokens=1-2 delims=: " %%i in ('time /t') do set mytime=%%i%%j
set DEV_TAG=dev-%mydate%-%mytime%

REM Build the image with dev tag
echo Building Docker image with dev tag: %DEV_TAG%...
docker build -t %DOCKER_USERNAME%/deletarr:%DEV_TAG% .

REM Push dev tag to Docker Hub
echo Pushing dev tag %DEV_TAG% to Docker Hub...
docker push %DOCKER_USERNAME%/deletarr:%DEV_TAG%

echo Successfully built and pushed dev version: %DEV_TAG%
echo.
echo To use in TrueNAS Scale, update your app to use: %DOCKER_USERNAME%/deletarr:%DEV_TAG%
pause