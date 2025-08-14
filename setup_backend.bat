@echo off
echo ========================================
echo StoryGen Backend Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "backend\manage.py" (
    echo ERROR: Please run this script from the storygen project root directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\Activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated: %VIRTUAL_ENV%
echo.

REM Navigate to backend directory
cd backend
echo Current directory: %CD%

REM Install Python dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Dependencies installed successfully.
echo.

REM Create media directories
echo Creating media directories...
if not exist "media" mkdir media
if not exist "media\characters" mkdir media\characters
if not exist "media\backgrounds" mkdir media\backgrounds
if not exist "media\merged" mkdir media\merged
echo Media directories created.
echo.

REM Run database migrations
echo Running database migrations...
python manage.py makemigrations
if errorlevel 1 (
    echo WARNING: Failed to create migrations (this might be normal for first run)
)

python manage.py migrate
if errorlevel 1 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo Database migrations completed.
echo.

REM Test the backend
echo Testing backend pipeline...
python manage.py test_pipeline --quick
if errorlevel 1 (
    echo WARNING: Pipeline test failed. This might be due to missing AI models.
    echo The first run will download models which may take some time.
)

echo.
echo ========================================
echo Backend Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Start the backend: cd backend ^& venv\Scripts\Activate.bat ^& python manage.py runserver
echo 2. Run setup_frontend.bat to set up the frontend
echo 3. Or run run_development.bat to start both servers
echo.
echo IMPORTANT: Always run Django commands from the backend directory!
echo Example: cd backend ^& python manage.py runserver
echo.
echo Note: First run may take longer as AI models are downloaded.
echo.
pause
