@echo off
echo ========================================
echo Git Setup and Push to GitHub
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo Step 1: Initializing Git repository...
git init

echo.
echo Step 2: Adding all files...
git add .

echo.
echo Step 3: Creating initial commit...
git commit -m "Initial commit: RAG-Powered Resume Builder"

echo.
echo Step 4: Setting default branch to main...
git branch -M main

echo.
echo ========================================
echo NEXT STEPS:
echo ========================================
echo 1. Go to GitHub.com and create a new repository
echo 2. Copy the repository URL (e.g., https://github.com/username/repo.git)
echo 3. Run this command (replace with your URL):
echo.
echo    git remote add origin YOUR_GITHUB_REPO_URL
echo    git push -u origin main
echo.
echo ========================================
pause
