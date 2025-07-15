#!/bin/bash
# TenxSOM AI Video Poller Runner
# Runs every 2 minutes to check video generation status

cd /home/golde/tenxsom-ai-vertex

# Load environment variables
export $(cat production.env | grep -v '^#' | xargs)

# Run the video poller
python3 poll_video_status.py >> video_poller.log 2>&1