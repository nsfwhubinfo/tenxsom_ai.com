#!/bin/bash

# Tenxsom AI Automated Monitoring System
# Designed for cron execution and webhook alerting

set -e

# Load configuration
if [ -f "/home/golde/tenxsom-ai-vertex/production-config.env" ]; then
    source /home/golde/tenxsom-ai-vertex/production-config.env
else
    echo "ERROR: production-config.env not found!"
    exit 1
fi

# Initialize variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${LOG_FILE:-/var/log/tenxsom-ai/monitor.log}"
STATE_FILE="${STATE_FILE:-/var/lib/tenxsom-ai/monitor.state}"
ALERT_COOLDOWN=3600  # 1 hour between identical alerts

# Ensure directories exist
mkdir -p "$(dirname "$LOG_FILE")" "$(dirname "$STATE_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Alert function with cooldown
send_alert() {
    local severity="$1"
    local component="$2"
    local message="$3"
    local alert_key="${severity}_${component}_$(echo "$message" | md5sum | cut -d' ' -f1)"
    local last_alert_file="$STATE_FILE.$alert_key"
    
    # Check cooldown
    if [ -f "$last_alert_file" ]; then
        local last_alert_time=$(cat "$last_alert_file")
        local current_time=$(date +%s)
        if (( current_time - last_alert_time < ALERT_COOLDOWN )); then
            log "Alert suppressed (cooldown): $message"
            return
        fi
    fi
    
    # Log alert
    log "[$severity] $component: $message"
    
    # Send webhook if configured
    if [ -n "$ALERT_WEBHOOK_URL" ]; then
        local payload=$(cat <<EOF
{
    "username": "Tenxsom AI Monitor",
    "icon_emoji": ":robot:",
    "attachments": [{
        "color": $([ "$severity" = "CRITICAL" ] && echo '"danger"' || echo '"warning"'),
        "title": "[$severity] $component Alert",
        "text": "$message",
        "timestamp": $(date +%s),
        "fields": [
            {"title": "Environment", "value": "${ENVIRONMENT:-production}", "short": true},
            {"title": "Host", "value": "$(hostname)", "short": true}
        ]
    }]
}
EOF
)
        curl -s -X POST -H 'Content-type: application/json' \
            --data "$payload" "$ALERT_WEBHOOK_URL" > /dev/null 2>&1 || \
            log "Failed to send webhook alert"
    fi
    
    # Update cooldown
    echo "$(date +%s)" > "$last_alert_file"
}

# Check UseAPI.net credit balance
check_credits() {
    log "Checking UseAPI.net credit balance..."
    
    local response=$(curl -s -H "Authorization: Bearer $USEAPI_BEARER_TOKEN" \
        "${USEAPI_BASE_URL}/accounts/credits" 2>/dev/null || echo '{"error": "API request failed"}')
    
    if echo "$response" | grep -q '"error"'; then
        send_alert "CRITICAL" "UseAPI" "Failed to fetch credit balance"
        return 1
    fi
    
    local credits=$(echo "$response" | jq -r '.credits // 0')
    log "Current credits: $credits"
    
    # Store for metrics
    echo "$credits" > "$STATE_FILE.credits"
    
    # Check thresholds
    if (( credits < ${CREDIT_CRITICAL_THRESHOLD:-1000} )); then
        send_alert "CRITICAL" "UseAPI" "Credit balance critical: $credits credits remaining"
    elif (( credits < ${CREDIT_WARNING_THRESHOLD:-5000} )); then
        send_alert "WARNING" "UseAPI" "Credit balance low: $credits credits remaining"
    fi
}

# Check agent health via HTTP endpoints
check_agent_health() {
    local agent_name="$1"
    local health_port="$2"
    
    log "Checking $agent_name health on port $health_port..."
    
    # Try health endpoint
    local response=$(curl -s -f -m 5 "http://localhost:$health_port/health" 2>/dev/null)
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        local status=$(echo "$response" | jq -r '.status // "unknown"' 2>/dev/null || echo "parse_error")
        if [ "$status" = "ok" ]; then
            log "$agent_name: Healthy"
            return 0
        else
            send_alert "WARNING" "$agent_name" "Agent responding but status is: $status"
            return 1
        fi
    else
        # Check if service is running via systemd
        if systemctl is-active --quiet "tenxsom-${agent_name,,}.service" 2>/dev/null; then
            send_alert "WARNING" "$agent_name" "Service running but health endpoint not responding on port $health_port"
        else
            send_alert "CRITICAL" "$agent_name" "Service is not running!"
        fi
        return 1
    fi
}

# Check all agents
check_all_agents() {
    local all_healthy=true
    
    check_agent_health "DeepAgent" "${DEEPAGENT_HEALTH_PORT:-8091}" || all_healthy=false
    check_agent_health "XPlatformExpert" "${X_PLATFORM_HEALTH_PORT:-8092}" || all_healthy=false
    check_agent_health "YouTubeExpert" "${YOUTUBE_HEALTH_PORT:-8093}" || all_healthy=false
    check_agent_health "TikTokExpert" "${TIKTOK_HEALTH_PORT:-8094}" || all_healthy=false
    check_agent_health "InstagramExpert" "${INSTAGRAM_HEALTH_PORT:-8095}" || all_healthy=false
    
    if [ "$all_healthy" = true ]; then
        log "All agents are healthy"
    fi
}

# Check video generation metrics
check_generation_metrics() {
    log "Checking video generation metrics..."
    
    # This would be expanded to check actual generation logs/database
    # For now, we'll check if the expected files exist
    local today=$(date +%Y-%m-%d)
    local metrics_file="$STATE_FILE.metrics.$today"
    
    if [ -f "$metrics_file" ]; then
        source "$metrics_file"
        
        # Check generation rate
        local expected_youtube=$(($(date +%H) / 2))  # Every 2 hours
        if (( ${YOUTUBE_VIDEOS_TODAY:-0} < expected_youtube - 2 )); then
            send_alert "WARNING" "Generation" "YouTube video generation behind schedule: ${YOUTUBE_VIDEOS_TODAY:-0}/$expected_youtube expected"
        fi
        
        # Check error rate
        if (( ${GENERATION_ERRORS_TODAY:-0} > 3 )); then
            send_alert "WARNING" "Generation" "High video generation error rate: ${GENERATION_ERRORS_TODAY} errors today"
        fi
    fi
}

# Calculate daily costs
check_daily_costs() {
    log "Checking daily costs..."
    
    local credits_file="$STATE_FILE.credits"
    local yesterday_file="$STATE_FILE.credits.yesterday"
    
    if [ -f "$credits_file" ] && [ -f "$yesterday_file" ]; then
        local current_credits=$(cat "$credits_file")
        local yesterday_credits=$(cat "$yesterday_file")
        local credits_used=$((yesterday_credits - current_credits))
        
        # Approximate cost calculation
        local daily_cost=$(echo "scale=2; $credits_used * 0.001" | bc)  # Assuming 1000 credits = $1
        
        log "Credits used in last 24h: $credits_used (~\$$daily_cost)"
        
        if (( $(echo "$daily_cost > ${DAILY_SPEND_LIMIT:-15.00}" | bc -l) )); then
            send_alert "WARNING" "Cost" "Daily spend limit exceeded: \$$daily_cost > \$${DAILY_SPEND_LIMIT}"
        fi
    fi
    
    # Rotate credits file
    if [ "$(date +%H:%M)" = "00:00" ]; then
        cp "$credits_file" "$yesterday_file" 2>/dev/null || true
    fi
}

# Main monitoring routine
main() {
    log "Starting Tenxsom AI monitoring check..."
    
    # Run all checks
    check_credits
    check_all_agents
    check_generation_metrics
    check_daily_costs
    
    # Update heartbeat
    echo "$(date +%s)" > "$STATE_FILE.heartbeat"
    
    log "Monitoring check completed"
}

# Execute main function
main "$@"