#!/bin/bash
# Setup script for local failover environment

echo "Setting up TenxsomAI Local Failover Environment"
echo "=============================================="

# Install Python dependencies
echo "Installing Python dependencies..."
pip install google-cloud-tasks google-cloud-logging requests

# Create necessary directories
echo "Creating required directories..."
mkdir -p monitoring/alerts flow_reports videos/output logs

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# TenxsomAI Local Environment Variables
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
CLOUD_TASKS_WORKER_URL=http://localhost:8081/process_video_job

# UseAPI.net
USEAPI_BEARER_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW
USEAPI_PRIMARY_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW
USEAPI_SECONDARY_1_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW

# Telegram
TELEGRAM_BOT_TOKEN=8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8
AUTHORIZED_USER_ID=8088003389

# YouTube API (update these with your credentials)
YOUTUBE_API_KEY=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=

# Database (for local MCP server)
DATABASE_URL=postgresql://postgres:password@localhost:5432/tenxsom_local

# Local ports
MCP_SERVER_PORT=8080
WORKER_PORT=8081
EOF
    echo ".env file created. Please update with your actual credentials."
fi

# Create systemd service for failover manager (optional)
echo "Creating systemd service file..."
cat > tenxsom-failover.service << EOF
[Unit]
Description=TenxsomAI Cloud Failover Manager
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
ExecStart=/usr/bin/python3 $PWD/cloud_failover_manager.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "Setup complete! Next steps:"
echo "1. Update .env file with your actual credentials"
echo "2. To run the failover manager: python3 cloud_failover_manager.py"
echo "3. To install as systemd service: sudo cp tenxsom-failover.service /etc/systemd/system/"
echo "4. To set up Telegram webhook: python3 setup_telegram_webhook.py"
echo ""
echo "The failover manager will:"
echo "- Monitor cloud services every 60 seconds"
echo "- Start local services after 3 consecutive cloud failures"
echo "- Switch back to cloud after 5 consecutive cloud successes"
echo "- Send Telegram alerts on failover events"