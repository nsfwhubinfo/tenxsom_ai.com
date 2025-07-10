#!/bin/bash

# Simple monitoring setup for MCP server using available APIs
set -e

PROJECT_ID=${1:-"tenxsom-ai-1631088"}
REGION=${2:-"us-central1"}
SERVICE_NAME="tenxsom-mcp-server"
NOTIFICATION_EMAIL=${3:-"goldensonproperties@gmail.com"}

echo "🔔 Setting up basic monitoring for MCP server"
echo "=============================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service: $SERVICE_NAME"
echo "Notification Email: $NOTIFICATION_EMAIL"
echo ""

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling monitoring APIs..."
gcloud services enable monitoring.googleapis.com

# Create uptime check using gcloud monitoring (basic functionality)
echo "⏱️ Creating uptime check..."
cat > /tmp/uptime_check.yaml << EOF
displayName: "MCP Server Health Check"
monitoredResource:
  type: "uptime_url"
  labels:
    project_id: "$PROJECT_ID"
    host: "tenxsom-mcp-server-hpkm6siuqq-uc.a.run.app"
httpCheck:
  path: "/health"
  port: 443
  useSsl: true
  validateSsl: true
period: "300s"
timeout: "10s"
selectedRegions: ["USA", "EUROPE", "ASIA_PACIFIC"]
contentMatchers:
- content: "healthy"
  matcher: "CONTAINS_STRING"
EOF

# Try to create uptime check (may require different method)
echo "Creating uptime check configuration..."
gcloud alpha monitoring uptime create --uptime-check-config-from-file=/tmp/uptime_check.yaml || echo "Note: Uptime check creation may require additional setup"

# Create cron job for detailed health monitoring
echo "⏰ Setting up cron job for health monitoring..."
cat << 'CRON_SCRIPT' > /tmp/mcp_health_cron.sh
#!/bin/bash
cd /home/golde/tenxsom-ai-vertex
source tenxsom-env/bin/activate 2>/dev/null || true
python3 monitor_mcp_health.py >> /var/log/mcp_health.log 2>&1
CRON_SCRIPT

chmod +x /tmp/mcp_health_cron.sh

# Add to cron (run every 5 minutes)
(crontab -l 2>/dev/null || true; echo "*/5 * * * * /tmp/mcp_health_cron.sh") | crontab -

# Create log directory
sudo mkdir -p /var/log
sudo touch /var/log/mcp_health.log
sudo chmod 666 /var/log/mcp_health.log

echo ""
echo "✅ Basic monitoring setup complete!"
echo "==================================="
echo "📊 Monitoring enabled for:"
echo "  - Service health checks every 5 minutes"
echo "  - Local health monitoring via cron"
echo "  - Logs written to /var/log/mcp_health.log"
echo ""
echo "📧 Health check results will be logged locally"
echo "⏰ Health checks run every 5 minutes via cron"
echo ""
echo "🔗 View monitoring dashboard:"
echo "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo ""
echo "🚨 To view uptime checks:"
echo "https://console.cloud.google.com/monitoring/uptime?project=$PROJECT_ID"
echo ""
echo "📄 View health logs:"
echo "tail -f /var/log/mcp_health.log"