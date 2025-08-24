#!/bin/bash

echo "🚀 Starting GPT-5 Payment Orchestration System"
echo "============================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start the server
echo ""
echo "✅ Server starting on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""
echo "To run the demo, open another terminal and run:"
echo "  python demo.py"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================"
echo ""

python main.py