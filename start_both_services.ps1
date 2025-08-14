# StoryGen Service Starter Script
Write-Host "🚀 Starting StoryGen Backend and Frontend..." -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not detected" -ForegroundColor Yellow
    Write-Host "   Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "✅ Virtual environment is active" -ForegroundColor Green
}

# Check if we're in the right directory
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: 'backend' directory not found!" -ForegroundColor Red
    Write-Host "   Please run this script from the project root directory" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: 'frontend' directory not found!" -ForegroundColor Red
    Write-Host "   Please run this script from the project root directory" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host "✅ Found both backend and frontend directories" -ForegroundColor Green

# Start backend in a new window
Write-Host ""
Write-Host "🔄 Starting Django Backend Server..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; python manage.py runserver 127.0.0.1:8000" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host ""
Write-Host "🎨 Starting React Frontend..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm start" -WindowStyle Normal

Write-Host ""
Write-Host "🎉 Both services are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "🎨 Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Keep these windows open to run the services" -ForegroundColor Cyan
Write-Host "   Close them when you're done" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"
