#!/bin/bash

echo "🚀 Starting GPT-5 Payment Router Server"
echo "======================================="
echo ""

# Check if venv exists
if [ ! -d "venv312" ]; then
    echo "Creating Python 3.12 virtual environment..."
    python3.12 -m venv venv312
    
    # Install dependencies
    source venv312/bin/activate
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
fi

# Activate and run
source venv312/bin/activate
echo "✅ Starting server on http://localhost:8000"
echo "📖 API docs at http://localhost:8000/docs"
echo ""
echo "To run demo: ./run_demo.sh"
echo "Press Ctrl+C to stop"
echo ""

python main.py