#!/bin/bash

# Startup script for Sembako Price API

echo "================================================"
echo "  Sembako Price API - Starting Server"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo "✓ Virtual environment activated"
echo ""

# Check if Chrome is installed (rough check)
if ! command -v google-chrome &> /dev/null && ! command -v chromium &> /dev/null && ! [ -d "/Applications/Google Chrome.app" ]; then
    echo "⚠️  Warning: Chrome might not be installed!"
    echo "   Selenium requires Chrome browser to work."
    echo ""
fi

echo "🚀 Starting Flask server..."
echo "   Server will be available at: http://localhost:5500"
echo "   Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Start the Flask app
python app.py
