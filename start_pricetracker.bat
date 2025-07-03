@echo off
REM start_pricetracker.bat - Windows startup script

echo ======================================
echo 🚀 PRICETRACKER STARTUP SCRIPT
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "backend\app.py" (
    echo ❌ Please run this script from the root directory of your PriceTracker project.
    pause
    exit /b 1
)

REM Install dependencies if requirements.txt exists
if exist "backend\requirements.txt" (
    echo 📦 Installing Python dependencies...
    pip install -r backend\requirements.txt
    
    echo 🌐 Installing Playwright browsers...
    playwright install chromium
)

echo.
echo Choose how to run PriceTracker:
echo.
echo 1^) 🌐 Web App Only ^(Manual price checking^)
echo 2^) 🤖 Background Service Only ^(Automatic checking^)
echo 3^) 🚀 Both Web App + Background Service ^(Recommended^)
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🌐 Starting PriceTracker Web Application...
    echo 💡 Access it at: http://localhost:5000
    echo ⏹️  Press Ctrl+C to stop
    echo.
    cd backend
    python app.py
) else if "%choice%"=="2" (
    echo.
    echo 🤖 Starting PriceTracker Background Service...
    echo 📦 Products: Checked every 6 hours
    echo 📈 Stocks: Checked every 5 minutes
    echo ⏹️  Press Ctrl+C to stop
    echo.
    cd backend
    python scheduler_service.py
) else if "%choice%"=="3" (
    echo.
    echo 🚀 Starting both Web App and Background Service...
    echo 💡 Web interface: http://localhost:5000
    echo 🤖 Background monitoring: Active
    echo ⏹️  Press Ctrl+C to stop both
    echo.
    
    REM Start background service
    cd backend
    start /B python scheduler_service.py
    
    REM Start web app
    python app.py
) else (
    echo ❌ Invalid choice. Please run the script again.
    pause
    exit /b 1
)

pause