#!/bin/bash
# start_pricetracker.sh - Complete startup script

echo "======================================"
echo "🚀 PRICETRACKER STARTUP SCRIPT"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ Please run this script from the root directory of your PriceTracker project."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "backend/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r backend/requirements.txt
    
    # Install Playwright browsers
    echo "🌐 Installing Playwright browsers..."
    playwright install chromium
fi

echo ""
echo "Choose how to run PriceTracker:"
echo ""
echo "1) 🌐 Web App Only (Manual price checking)"
echo "2) 🤖 Background Service Only (Automatic checking)"
echo "3) 🚀 Both Web App + Background Service (Recommended)"
echo ""
read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Starting PriceTracker Web Application..."
        echo "💡 Access it at: http://localhost:5000"
        echo "⏹️  Press Ctrl+C to stop"
        echo ""
        cd backend && python3 app.py
        ;;
    2)
        echo ""
        echo "🤖 Starting PriceTracker Background Service..."
        echo "📦 Products: Checked every 6 hours"
        echo "📈 Stocks: Checked every 5 minutes"
        echo "⏹️  Press Ctrl+C to stop"
        echo ""
        cd backend && python3 scheduler_service.py
        ;;
    3)
        echo ""
        echo "🚀 Starting both Web App and Background Service..."
        echo "💡 Web interface: http://localhost:5000"
        echo "🤖 Background monitoring: Active"
        echo "⏹️  Press Ctrl+C to stop both"
        echo ""
        
        # Start background service in the background
        cd backend && python3 scheduler_service.py &
        SCHEDULER_PID=$!
        
        # Start web app in foreground
        python3 app.py &
        WEB_PID=$!
        
        # Wait for either to exit
        wait $WEB_PID $SCHEDULER_PID
        
        # Clean up
        kill $SCHEDULER_PID 2>/dev/null
        kill $WEB_PID 2>/dev/null
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac