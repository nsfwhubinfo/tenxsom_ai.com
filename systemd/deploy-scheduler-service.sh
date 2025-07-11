#!/bin/bash

# Deploy TenxsomAI Scheduler as systemd service
set -e

echo "🚀 Deploying TenxsomAI Scheduler as systemd service..."

# Check if running as root/sudo
if [[ $EUID -eq 0 ]]; then
    echo "❌ This script should NOT be run as root"
    echo "Please run as the tenxsom user with sudo for systemctl commands"
    exit 1
fi

# Define paths
SERVICE_FILE="/home/golde/tenxsom-ai-vertex/systemd/tenxsom-scheduler.service"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_NAME="tenxsom-scheduler.service"

# Check if service file exists
if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "❌ Service file not found: $SERVICE_FILE"
    exit 1
fi

# Check if production config exists
if [[ ! -f "/home/golde/tenxsom-ai-vertex/production-config.env" ]]; then
    echo "⚠️ Production config not found. Creating from template..."
    if [[ -f "/home/golde/tenxsom-ai-vertex/production-config.env.template" ]]; then
        cp "/home/golde/tenxsom-ai-vertex/production-config.env.template" "/home/golde/tenxsom-ai-vertex/production-config.env"
        echo "📄 Created production-config.env from template"
        echo "⚠️ Please edit production-config.env with your actual credentials before starting"
    else
        echo "❌ No production config template found"
        exit 1
    fi
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p /home/golde/tenxsom-ai-vertex/logs
touch /home/golde/tenxsom-ai-vertex/logs/scheduler_production.log
chmod 664 /home/golde/tenxsom-ai-vertex/logs/scheduler_production.log

# Copy service file to systemd
echo "📄 Installing systemd service file..."
sudo cp "$SERVICE_FILE" "$SYSTEMD_DIR/$SERVICE_NAME"
sudo chown root:root "$SYSTEMD_DIR/$SERVICE_NAME"
sudo chmod 644 "$SYSTEMD_DIR/$SERVICE_NAME"

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service (but don't start yet)
echo "⚙️ Enabling service..."
sudo systemctl enable "$SERVICE_NAME"

# Check service status
echo "📊 Service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager || true

echo ""
echo "✅ TenxsomAI Scheduler service deployed successfully!"
echo ""
echo "📋 Service Management Commands:"
echo "   Start:   sudo systemctl start $SERVICE_NAME"
echo "   Stop:    sudo systemctl stop $SERVICE_NAME"
echo "   Status:  sudo systemctl status $SERVICE_NAME"
echo "   Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "🔧 Next Steps:"
echo "   1. Edit /home/golde/tenxsom-ai-vertex/production-config.env with your credentials"
echo "   2. Test the service: sudo systemctl start $SERVICE_NAME"
echo "   3. Monitor logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "⚠️  IMPORTANT: Service will fail until production-config.env is properly configured!"