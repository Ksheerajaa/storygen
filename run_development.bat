@echo off
echo ========================================
echo StoryGen Development Server Launcher
echo ========================================
echo.
echo This script will start both the Django backend and React frontend.
echo.
echo Prerequisites:
echo - Backend must be set up (run setup_backend.bat first)
echo - Frontend must be set up (run setup_frontend.bat first)
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found.
    echo Please run setup_backend.bat first.
    pause
    exit /b 1
)

REM Check if frontend dependencies exist
if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies not found.
    echo Please run setup_frontend.bat first.
    pause
    exit /b 1
)

echo Starting StoryGen development servers...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Press Ctrl+C in either terminal to stop the servers.
echo.

REM Start backend server in new terminal
echo Starting Django backend server...
start "StoryGen Backend" cmd /k "cd /d %CD% && venv\Scripts\Activate.bat && cd backend && python manage.py runserver"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in new terminal
echo Starting React frontend server...
start "StoryGen Frontend" cmd /k "cd /d %CD% && cd frontend && npm start"

echo.
echo ========================================
echo Servers Started Successfully!
echo ========================================
echo.
echo Backend: http://localhost:8000 (Terminal 1)
echo Frontend: http://localhost:3000 (Terminal 2)
echo.
echo Both servers are now running in separate terminals.
echo Close the terminals to stop the servers.
echo.
echo Your browser should open automatically to the frontend.
echo If not, manually navigate to: http://localhost:3000
echo.
echo Note: First run may take longer as AI models are downloaded.
echo.
pause
