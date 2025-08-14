@echo off
echo ========================================
echo StoryGen Frontend Setup Script
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm is not installed or not in PATH
    echo Please install Node.js which includes npm
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "frontend\package.json" (
    echo ERROR: Please run this script from the storygen project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Node.js found. Checking versions...
node --version
npm --version
echo.

REM Navigate to frontend directory
cd frontend

REM Check if node_modules already exists
if exist "node_modules" (
    echo Node modules already exist. Checking if update is needed...
    echo.
    echo Current dependencies:
    npm list --depth=0
    echo.
    set /p choice="Do you want to reinstall dependencies? (y/N): "
    if /i "%choice%"=="y" (
        echo Removing existing node_modules...
        rmdir /s /q node_modules
        if exist "package-lock.json" del package-lock.json
    ) else (
        echo Skipping dependency installation.
        goto :test_frontend
    )
)

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully.
echo.

:test_frontend
REM Test the frontend
echo Testing frontend...
echo Starting development server (will open browser)...
echo Press Ctrl+C to stop the server when it opens.
echo.

REM Start the development server
npm start

echo.
echo ========================================
echo Frontend Setup Complete!
echo ========================================
echo.
echo The React development server should have opened in your browser.
echo If not, manually navigate to: http://localhost:3000
echo.
echo Next steps:
echo 1. Ensure the backend is running (cd backend ^& venv\Scripts\Activate.bat ^& python manage.py runserver)
echo 2. Or run run_development.bat to start both servers
echo.
pause
