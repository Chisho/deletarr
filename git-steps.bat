@echo off

:: Stage all changes
echo Staging all changes...
git add .
pause

:: Request commit message
echo Enter commit message:
set /p COMMIT_MSG="Commit message: "
git commit -m "%COMMIT_MSG%"
pause

:: Push to remote
echo Pushing to remote...
git push
pause

:: Tagging
echo Creating a new tag...
echo Current Version: 
type version.txt
echo.
set /p TAG="Enter tag name (e.g., 0.1.0): "
set TAG=v%TAG%
git tag %TAG%
echo %TAG% > version.txt
echo version.txt updated to %TAG%
pause

:: Push tag
echo Pushing tag to remote...
git push origin %TAG%

echo All done!
pause