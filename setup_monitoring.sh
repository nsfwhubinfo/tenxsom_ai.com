#!/bin/bash

# Setup monitoring and alerting for MCP server
# This script configures Google Cloud Monitoring and alerting

set -e

PROJECT_ID=${1:-"tenxsom-ai-1631088"}
REGION=${2:-"us-central1"}
SERVICE_NAME="tenxsom-mcp-server"
NOTIFICATION_EMAIL=${3:-"goldensonproperties@gmail.com"}

echo "🔔 Setting up monitoring and alerting for MCP server"
echo "=================================================="
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
gcloud services enable alertpolicy.googleapis.com
gcloud services enable cloudtrace.googleapis.com

# Create notification channel for email alerts
echo "📧 Creating notification channel..."
NOTIFICATION_CHANNEL_JSON=$(cat <<EOF
{
  "type": "email",
  "displayName": "MCP Server Alerts",
  "description": "Email notifications for MCP server issues",
  "labels": {
    "email_address": "$NOTIFICATION_EMAIL"
  },
  "enabled": true
}
EOF
)

# Create the notification channel
NOTIFICATION_CHANNEL_ID=$(gcloud alpha monitoring channels create \
  --channel-content="$NOTIFICATION_CHANNEL_JSON" \
  --format="value(name)" | cut -d'/' -f6)

echo "✅ Created notification channel: $NOTIFICATION_CHANNEL_ID"

# Create alerting policies
echo "🚨 Creating alerting policies..."

# 1. High error rate alert
HIGH_ERROR_RATE_POLICY=$(cat <<EOF
{
  "displayName": "MCP Server - High Error Rate",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "Error rate > 5%",
      "conditionThreshold": {
        "filter": "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"$SERVICE_NAME\"",
        "comparison": "COMPARISON_GREATER_THAN",
        "thresholdValue": 0.05,
        "duration": "300s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_RATE",
            "crossSeriesReducer": "REDUCE_MEAN",
            "groupByFields": ["resource.label.service_name"]
          }
        ]
      }
    }
  ],
  "notificationChannels": [
    "projects/$PROJECT_ID/notificationChannels/$NOTIFICATION_CHANNEL_ID"
  ],
  "alertStrategy": {
    "autoClose": "86400s"
  }
}
EOF
)

gcloud alpha monitoring policies create --policy-from-file=<(echo "$HIGH_ERROR_RATE_POLICY") || true

# 2. High response time alert
HIGH_LATENCY_POLICY=$(cat <<EOF
{
  "displayName": "MCP Server - High Response Time",
  "combiner": "OR", 
  "conditions": [
    {
      "displayName": "95th percentile latency > 5s",
      "conditionThreshold": {
        "filter": "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"$SERVICE_NAME\"",
        "comparison": "COMPARISON_GREATER_THAN",
        "thresholdValue": 5000,
        "duration": "300s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_DELTA",
            "crossSeriesReducer": "REDUCE_PERCENTILE_95",
            "groupByFields": ["resource.label.service_name"]
          }
        ]
      }
    }
  ],
  "notificationChannels": [
    "projects/$PROJECT_ID/notificationChannels/$NOTIFICATION_CHANNEL_ID"
  ],
  "alertStrategy": {
    "autoClose": "86400s"
  }
}
EOF
)

gcloud alpha monitoring policies create --policy-from-file=<(echo "$HIGH_LATENCY_POLICY") || true

# 3. Service availability alert
SERVICE_DOWN_POLICY=$(cat <<EOF
{
  "displayName": "MCP Server - Service Down",
  "combiner": "OR",
  "conditions": [
    {
      "displayName": "No requests received in 10 minutes",
      "conditionAbsent": {
        "filter": "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"$SERVICE_NAME\"",
        "duration": "600s",
        "aggregations": [
          {
            "alignmentPeriod": "60s",
            "perSeriesAligner": "ALIGN_RATE",
            "crossSeriesReducer": "REDUCE_SUM",
            "groupByFields": ["resource.label.service_name"]
          }
        ]
      }
    }
  ],
  "notificationChannels": [
    "projects/$PROJECT_ID/notificationChannels/$NOTIFICATION_CHANNEL_ID"
  ],
  "alertStrategy": {
    "autoClose": "86400s"
  }
}
EOF
)

gcloud alpha monitoring policies create --policy-from-file=<(echo "$SERVICE_DOWN_POLICY") || true

# Create uptime check
echo "⏱️ Creating uptime check..."
UPTIME_CHECK_JSON=$(cat <<EOF
{
  "displayName": "MCP Server Health Check",
  "monitoredResource": {
    "type": "uptime_url",
    "labels": {
      "project_id": "$PROJECT_ID",
      "host": "tenxsom-mcp-server-hpkm6siuqq-uc.a.run.app"
    }
  },
  "httpCheck": {
    "path": "/health",
    "port": 443,
    "useSsl": true,
    "validateSsl": true
  },
  "period": "300s",
  "timeout": "10s",
  "selectedRegions": ["USA", "EUROPE", "ASIA_PACIFIC"],
  "contentMatchers": [
    {
      "content": "healthy",
      "matcher": "CONTAINS_STRING"
    }
  ]
}
EOF
)

gcloud monitoring uptime create --uptime-check-config="$UPTIME_CHECK_JSON" || true

# Create cron job for detailed health monitoring
echo "⏰ Setting up cron job for health monitoring..."
cat << 'CRON_SCRIPT' > /tmp/mcp_health_cron.sh
#!/bin/bash
cd /home/golde/tenxsom-ai-vertex
source tenxsom-env/bin/activate
python3 monitor_mcp_health.py >> /var/log/mcp_health.log 2>&1
CRON_SCRIPT

chmod +x /tmp/mcp_health_cron.sh

# Add to cron (run every 5 minutes)
(crontab -l 2>/dev/null || true; echo "*/5 * * * * /tmp/mcp_health_cron.sh") | crontab -

echo ""
echo "✅ Monitoring setup complete!"
echo "=========================="
echo "📊 Monitoring enabled for:"
echo "  - Error rate > 5%"
echo "  - Response time > 5s"
echo "  - Service availability"
echo "  - Uptime checks every 5 minutes"
echo ""
echo "📧 Alerts will be sent to: $NOTIFICATION_EMAIL"
echo "⏰ Health checks run every 5 minutes via cron"
echo ""
echo "🔗 View monitoring dashboard:"
echo "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
echo ""
echo "🚨 View alert policies:"
echo "https://console.cloud.google.com/monitoring/alerting?project=$PROJECT_ID"