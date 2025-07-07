#!/bin/bash

# Tenxsom AI Production Quick Start Script
# One-command production system startup

set -e

echo "🚀 Tenxsom AI Production Quick Start"
echo "===================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "tenxsom-env" ]; then
    echo "🐍 Activating virtual environment..."
    source tenxsom-env/bin/activate
else
    echo "⚠️  Virtual environment not found"
    echo "   Creating virtual environment and installing dependencies..."
    python3 -m venv tenxsom-env
    source tenxsom-env/bin/activate
    pip install python-telegram-bot psutil structlog python-dotenv requests aiohttp > /dev/null 2>&1
    echo "✅ Virtual environment created and dependencies installed"
fi

# Check if we're in the right directory
if [ ! -f "production_startup.py" ]; then
    echo "❌ Error: production_startup.py not found"
    echo "Please run this script from the Tenxsom AI project root directory"
    exit 1
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env"
    # Use safer method to load environment variables, filtering out comments and empty lines
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ "$line" =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
            continue
        fi
        # Export valid variable assignments
        if [[ "$line" =~ ^[A-Za-z_][A-Za-z0-9_]*= ]]; then
            export "$line"
        fi
    done < .env
else
    echo "⚠️  Warning: .env file not found"
    echo "   Make sure to set required environment variables manually"
fi

# Check for required environment variables
REQUIRED_VARS=("USEAPI_BEARER_TOKEN" "YOUTUBE_API_KEY" "GOOGLE_APPLICATION_CREDENTIALS" "TELEGRAM_BOT_TOKEN")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Error: Missing required environment variables:"
    printf '   %s\n' "${MISSING_VARS[@]}"
    echo ""
    echo "💡 Set these variables in your .env file or export them manually"
    exit 1
fi

# Create production directories
echo "📁 Creating production directories..."
mkdir -p production/{logs,backups,monitoring,reports,startup}

# Parse command line arguments
COMMAND=${1:-start}
EXTRA_ARGS=""

if [ "$2" = "--no-optional" ]; then
    EXTRA_ARGS="--no-optional"
fi

# Execute the command
echo "🎯 Executing: $COMMAND"
echo ""

case $COMMAND in
    "start")
        echo "🚀 Starting Tenxsom AI Production System..."
        python3 production_startup.py start $EXTRA_ARGS
        ;;
    "stop")
        echo "🛑 Stopping Tenxsom AI Production System..."
        python3 production_startup.py stop
        ;;
    "restart")
        echo "🔄 Restarting Tenxsom AI Production System..."
        python3 production_startup.py restart $EXTRA_ARGS
        ;;
    "status")
        echo "📊 Checking System Status..."
        python3 production_startup.py status
        ;;
    "health")
        echo "🏥 Running Health Check..."
        python3 production_startup.py health
        ;;
    "logs")
        echo "📄 Showing Recent Logs..."
        if [ -d "production/logs" ]; then
            find production/logs -name "*.log" -type f -exec tail -20 {} +
        else
            echo "No log files found"
        fi
        ;;
    "test")
        echo "🧪 Running System Test..."
        python3 end_to_end_pipeline_test.py
        ;;
    "deploy")
        echo "🚀 Running Production Deployment..."
        python3 production_deployment.py
        ;;
    *)
        echo "❌ Unknown command: $COMMAND"
        echo ""
        echo "📖 Available commands:"
        echo "   start     - Start the production system"
        echo "   stop      - Stop the production system"
        echo "   restart   - Restart the production system"
        echo "   status    - Show system status"
        echo "   health    - Run health check"
        echo "   logs      - Show recent logs"
        echo "   test      - Run end-to-end test"
        echo "   deploy    - Run production deployment"
        echo ""
        echo "🔧 Options:"
        echo "   --no-optional  - Skip optional services during start/restart"
        echo ""
        echo "📋 Examples:"
        echo "   ./quick_start.sh start"
        echo "   ./quick_start.sh start --no-optional"
        echo "   ./quick_start.sh status"
        echo "   ./quick_start.sh test"
        exit 1
        ;;
esac

echo ""
echo "✅ Command completed!"

# Show helpful information for start command
if [ "$COMMAND" = "start" ]; then
    echo ""
    echo "🔧 Quick Management Commands:"
    echo "   ./quick_start.sh status    - Check system status"
    echo "   ./quick_start.sh stop      - Stop the system"
    echo "   ./quick_start.sh logs      - View recent logs"
    echo ""
    echo "📊 Monitor system:"
    echo "   tail -f production/logs/*.log"
    echo ""
    echo "🎯 System ready for 30-day monetization strategy execution!"
fi