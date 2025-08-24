#!/bin/bash

echo "🚀 GPT-5 Payment Orchestration Demo"
echo "===================================="
echo ""

# Check if server is running
curl -s http://localhost:8000/ > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Server not running. Please run './start_server.sh' first"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Activate virtual environment
source venv312/bin/activate

# Run demo
python demo.py << EOF
n
EOF