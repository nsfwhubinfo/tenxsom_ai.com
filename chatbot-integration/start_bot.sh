#!/bin/bash
# TenxsomAI Telegram Bot Startup Script

export TELEGRAM_BOT_TOKEN="8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8"
export AUTHORIZED_USER_ID="8088003389"  
export USEAPI_BEARER_TOKEN="user:1831-r8vA1WGayarXKuYwpT1PW"
export GOOGLE_CLOUD_PROJECT="tenxsom-ai-1631088"

echo "🤖 Starting TenxsomAI Telegram Bot..."
echo "Bot: @TenxsomAI_bot"
echo "User ID: $AUTHORIZED_USER_ID"
echo "Time: $(date)"
echo "======================================"

# Start the bot in background
nohup python3 central-controller.py > telegram_bot.log 2>&1 &
BOT_PID=$!

echo "✅ Bot started with PID: $BOT_PID"
echo "📋 Log file: telegram_bot.log"
echo "🔍 Check status: ps aux | grep $BOT_PID"
echo "🛑 Stop bot: kill $BOT_PID"

# Save PID for easy management
echo $BOT_PID > bot.pid
echo "💾 PID saved to bot.pid"