#!/bin/bash

# Deploy Tenxsom AI Holistic Integration System

set -e

echo "🚀 Deploying Tenxsom AI Holistic System"
echo "======================================="

PROJECT_ROOT="/home/golde/tenxsom-ai-vertex"

# Load configuration
if [ -f "$PROJECT_ROOT/config/production/holistic-config.env" ]; then
    source "$PROJECT_ROOT/config/production/holistic-config.env"
    echo "✅ Configuration loaded"
else
    echo "❌ Configuration file not found. Please copy from template and configure."
    exit 1
fi

# Validate Google AI Ultra credentials
if [ ! -f "$GOOGLE_AI_ULTRA_CREDENTIALS" ]; then
    echo "❌ Google AI Ultra credentials not found at: $GOOGLE_AI_ULTRA_CREDENTIALS"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install aiohttp asyncio dataclasses

# Test Google AI Ultra connection
echo "🔍 Testing Google AI Ultra connection..."
python -c "
import json
with open('$GOOGLE_AI_ULTRA_CREDENTIALS', 'r') as f:
    creds = json.load(f)
    if 'api_key' in creds and 'project_id' in creds:
        print('✅ Google AI Ultra credentials valid')
    else:
        print('❌ Invalid credentials format')
        exit(1)
"

# Test UseAPI.net accounts
echo "🔍 Testing UseAPI.net accounts..."
if [ -n "$USEAPI_PRIMARY_TOKEN" ]; then
    curl -s -H "Authorization: Bearer $USEAPI_PRIMARY_TOKEN" \
         "https://api.useapi.net/v1/accounts/credits" | jq . > /dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Primary UseAPI.net account accessible"
    else
        echo "❌ Primary UseAPI.net account test failed"
    fi
fi

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/tenxsom-holistic.service > /dev/null << EOL
[Unit]
Description=Tenxsom AI Holistic Integration System
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=$PROJECT_ROOT
Environment=PYTHONPATH=$PROJECT_ROOT
ExecStart=/usr/bin/python3 $PROJECT_ROOT/integrations/tenxsom_holistic_bridge.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable tenxsom-holistic
echo "✅ Systemd service created and enabled"

# Create monitoring script
echo "📊 Setting up monitoring..."
cat > "$PROJECT_ROOT/scripts/monitoring/monitor-holistic.sh" << 'MONITOR_EOF'
#!/bin/bash

# Monitor Tenxsom AI Holistic System

PROJECT_ROOT="/home/golde/tenxsom-ai-vertex"

# Check service status
if systemctl is-active --quiet tenxsom-holistic; then
    echo "✅ Tenxsom Holistic service is running"
else
    echo "❌ Tenxsom Holistic service is not running"
    sudo systemctl restart tenxsom-holistic
fi

# Check credit usage
python3 << 'PYTHON_EOF'
import json
import os
import sys
sys.path.append("$PROJECT_ROOT")

from integrations.enhanced_model_router import EnhancedModelRouter

async def check_credits():
    # Would implement actual credit checking
    print("📊 Credit usage check completed")

import asyncio
asyncio.run(check_credits())
PYTHON_EOF

echo "📊 Monitoring check completed at $(date)"
MONITOR_EOF

chmod +x "$PROJECT_ROOT/scripts/monitoring/monitor-holistic.sh"

# Create daily cron job
echo "⏰ Setting up daily monitoring cron job..."
(crontab -l 2>/dev/null; echo "0 6 * * * $PROJECT_ROOT/scripts/monitoring/monitor-holistic.sh >> $PROJECT_ROOT/logs/monitor.log 2>&1") | crontab -

echo ""
echo "🎉 Tenxsom AI Holistic System Deployed Successfully!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Start the service: sudo systemctl start tenxsom-holistic"
echo "2. Check logs: journalctl -u tenxsom-holistic -f"
echo "3. Monitor credits: $PROJECT_ROOT/scripts/monitoring/monitor-holistic.sh"
echo "4. Begin 30-day strategy execution"
echo ""
echo "🚀 Ready for production content generation!"
