@echo off
setlocal enabledelayedexpansion

if "%DOCKER_USERNAME%"=="" (
    echo Error: DOCKER_USERNAME environment variable is not set
    echo Usage: set DOCKER_USERNAME=yourusername ^& push-dev.bat
    exit /b 1
)

REM Use current timestamp for unique dev tag
for /f "tokens=1-4 delims=/ " %%i in ('date /t') do set mydate=%%i-%%j-%%k
for /f "tokens=1-2 delims=: " %%i in ('time /t') do set mytime=%%i%%j
set DEV_TAG=dev-%mydate%-%mytime%

echo --- GIT STEPS ---
echo Staging changes...
git add .

echo Commiting changes...
git commit -m "Dev push: %DEV_TAG%"

echo Pushing to Git...
git push

echo --- DOCKER STEPS ---
echo Building Docker image with dev tag: %DEV_TAG%...
docker build -t %DOCKER_USERNAME%/deletarr:%DEV_TAG% .

echo Pushing dev tag %DEV_TAG% to Docker Hub...
docker push %DOCKER_USERNAME%/deletarr:%DEV_TAG%

echo --------------------------------------------------
echo Successfully pushed to Git and Docker (Tag: %DEV_TAG%)
echo --------------------------------------------------
pause
