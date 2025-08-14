@echo off
echo 🚀 Starting StoryGen Backend...
echo ==================================================

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo ⚠️  Virtual environment not detected
    echo    Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ✅ Virtual environment is active
)

REM Check if we're in the right directory
if not exist "backend" (
    echo ❌ Error: 'backend' directory not found!
    echo    Please run this script from the project root directory
    pause
    exit /b 1
)

REM Change to backend directory
cd backend

REM Check if manage.py exists
if not exist "manage.py" (
    echo ❌ Error: 'manage.py' not found in backend directory!
    pause
    exit /b 1
)

echo ✅ Found Django project
echo 📍 Working directory: %CD%

echo.
echo 🔄 Starting Django development server...
echo    Server will be available at: http://localhost:8000
echo    Press Ctrl+C to stop the server
echo --------------------------------------------------

REM Start the server
python manage.py runserver 0.0.0.0:8000

echo.
echo 🛑 Server stopped
pause
