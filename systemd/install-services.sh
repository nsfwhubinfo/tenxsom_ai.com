#!/bin/bash

# Systemd Service Installation Script for Tenxsom AI
# This script creates and installs systemd services for all agents

set -e

echo "🚀 Installing Tenxsom AI systemd services"

# Check if running with appropriate permissions
if [ "$EUID" -ne 0 ]; then 
    echo "Please run with sudo: sudo $0"
    exit 1
fi

# Define agents with their configurations
declare -A AGENTS=(
    ["deepagent"]="DeepAgent|/home/golde/Tenxsom_AI/TenxsomAI-Main/agents/DeepAgent|main.py|8091"
    ["x_platform_expert"]="XPlatformExpert|/home/golde/Tenxsom_AI/TenxsomAI-Main/agents|x_platform_expert.py|8092"
    ["youtube_expert"]="YouTubeExpert|/home/golde/Tenxsom_AI/TenxsomAI-Main/agents/YouTube_Expert|main.py|8093"
    ["tiktok_expert"]="TikTokExpert|/home/golde/Tenxsom_AI/TenxsomAI-Main/agents/TikTok_Expert|main.py|8094"
    ["instagram_expert"]="InstagramExpert|/home/golde/Tenxsom_AI/TenxsomAI-Main/agents/Instagram_Expert|main.py|8095"
)

# Create services directory if not exists
mkdir -p /etc/systemd/system/

# Generate service files
for service_name in "${!AGENTS[@]}"; do
    IFS='|' read -r agent_name working_dir main_script health_port <<< "${AGENTS[$service_name]}"
    
    echo "Creating service: tenxsom-${service_name}.service"
    
    # Copy template and replace placeholders
    sed -e "s|{{AgentName}}|${agent_name}|g" \
        -e "s|{{User}}|golde|g" \
        -e "s|{{Group}}|golde|g" \
        -e "s|{{WorkingDirectory}}|${working_dir}|g" \
        -e "s|{{MainScriptPath}}|${main_script}|g" \
        -e "s|{{HealthPort}}|${health_port}|g" \
        tenxsom-agent-template.service > "/etc/systemd/system/tenxsom-${service_name}.service"
done

# Create a target to manage all services as a group
cat > /etc/systemd/system/tenxsom-ai.target << EOF
[Unit]
Description=Tenxsom AI Production System
Documentation=file:///home/golde/tenxsom-ai-vertex/PRODUCTION-INTEGRATION-SUMMARY.md
After=network-online.target
Wants=network-online.target

[Install]
WantedBy=multi-user.target
EOF

# Update each service to be wanted by the target
for service_name in "${!AGENTS[@]}"; do
    echo "WantedBy=tenxsom-ai.target" >> "/etc/systemd/system/tenxsom-${service_name}.service"
done

# Reload systemd
systemctl daemon-reload

echo "✅ Services installed successfully!"
echo ""
echo "📋 Available commands:"
echo "   Start all agents:    sudo systemctl start tenxsom-ai.target"
echo "   Stop all agents:     sudo systemctl stop tenxsom-ai.target"
echo "   Enable on boot:      sudo systemctl enable tenxsom-ai.target"
echo "   Check status:        sudo systemctl status 'tenxsom-*'"
echo ""
echo "   Individual control:  sudo systemctl [start|stop|status] tenxsom-deepagent.service"