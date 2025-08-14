@echo off
echo 🚀 Starting StoryGen Backend and Frontend...
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

if not exist "frontend" (
    echo ❌ Error: 'frontend' directory not found!
    echo    Please run this script from the project root directory
    pause
    exit /b 1
)

echo ✅ Found both backend and frontend directories

REM Start backend in a new window
echo.
echo 🔄 Starting Django Backend Server...
start "StoryGen Backend" cmd /k "cd backend && python manage.py runserver 127.0.0.1:8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in a new window
echo.
echo 🎨 Starting React Frontend...
start "StoryGen Frontend" cmd /k "cd frontend && npm start"

echo.
echo 🎉 Both services are starting!
echo.
echo 📍 Backend: http://127.0.0.1:8000
echo 🎨 Frontend: http://localhost:3000
echo.
echo 💡 Keep these windows open to run the services
echo    Close them when you're done
echo.
pause
