#!/bin/bash
# TenxsomAI Telegram Bot Manager

BOT_PID_FILE="bot.pid"
BOT_LOG_FILE="telegram_bot.log"

case "$1" in
    start)
        if [ -f "$BOT_PID_FILE" ] && kill -0 $(cat "$BOT_PID_FILE") 2>/dev/null; then
            echo "❌ Bot is already running (PID: $(cat $BOT_PID_FILE))"
            exit 1
        fi
        echo "🚀 Starting TenxsomAI Telegram Bot..."
        ./start_bot.sh
        ;;
    
    stop)
        if [ -f "$BOT_PID_FILE" ]; then
            PID=$(cat "$BOT_PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                rm -f "$BOT_PID_FILE"
                echo "🛑 Bot stopped (PID: $PID)"
            else
                echo "❌ Bot not running (stale PID file removed)"
                rm -f "$BOT_PID_FILE"
            fi
        else
            echo "❌ Bot not running (no PID file)"
        fi
        ;;
    
    status)
        if [ -f "$BOT_PID_FILE" ]; then
            PID=$(cat "$BOT_PID_FILE")
            if kill -0 "$PID" 2>/dev/null; then
                echo "✅ Bot is running (PID: $PID)"
                echo "📱 Bot: @TenxsomAI_bot"
                echo "👤 Authorized User: $AUTHORIZED_USER_ID"
                echo "⏰ Started: $(ps -o lstart= -p $PID)"
                echo "📊 Memory: $(ps -o rss= -p $PID | awk '{print int($1/1024) "MB"}')"
            else
                echo "❌ Bot not running (stale PID file)"
                rm -f "$BOT_PID_FILE"
            fi
        else
            echo "❌ Bot not running"
        fi
        ;;
    
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    
    logs)
        if [ -f "$BOT_LOG_FILE" ]; then
            echo "📋 Last 20 lines of bot logs:"
            echo "=============================="
            tail -20 "$BOT_LOG_FILE"
        else
            echo "❌ No log file found"
        fi
        ;;
    
    follow)
        if [ -f "$BOT_LOG_FILE" ]; then
            echo "📋 Following bot logs (Ctrl+C to exit):"
            echo "======================================="
            tail -f "$BOT_LOG_FILE"
        else
            echo "❌ No log file found"
        fi
        ;;
    
    test)
        echo "🧪 Testing bot connectivity..."
        curl -s "https://api.telegram.org/bot8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8/getMe" | jq '.result | {id, username, first_name}'
        ;;
    
    *)
        echo "TenxsomAI Telegram Bot Manager"
        echo "=============================="
        echo "Usage: $0 {start|stop|restart|status|logs|follow|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the bot"
        echo "  stop    - Stop the bot"
        echo "  restart - Restart the bot"
        echo "  status  - Show bot status"
        echo "  logs    - Show recent logs"
        echo "  follow  - Follow logs in real-time"
        echo "  test    - Test bot API connectivity"
        exit 1
        ;;
esac