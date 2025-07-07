#!/bin/bash

# Tenxsom AI Chatbot Startup Script

echo "🤖 Starting Tenxsom AI Chatbot..."

# Change to chatbot directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import telegram" 2>/dev/null; then
    echo "📦 Installing core dependencies..."
    pip install python-telegram-bot httpx python-dotenv asyncio-throttle
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if bot token is configured
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "YOUR_BOT_TOKEN_FROM_BOTFATHER" ]; then
    echo "❌ Please configure TELEGRAM_BOT_TOKEN in .env file"
    exit 1
fi

echo "✅ Configuration loaded"
echo "🚀 Starting chatbot with bot: @TenxsomAI_bot"
echo "📱 Authorized User ID: 8088003389"
echo ""

# Start the chatbot
python central-controller.py