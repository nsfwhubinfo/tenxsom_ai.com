# TenxsomAI Production System - Claude Code Context

This file contains critical information for Claude Code sessions to maintain contextual memory persistence.

## Project Overview

TenxsomAI is a comprehensive AI-powered video generation and content distribution system that:
- Generates 96 videos per day across multiple platforms (YouTube, TikTok, Instagram, X)
- Uses Google Cloud Tasks for job orchestration (replaced Redis)
- Integrates multiple AI services via UseAPI.net
- Provides Telegram bot interface for system control
- Features AI-powered monitoring and intelligent decision making

## Critical Resolutions

### 1. UseAPI.net Endpoint Migration (2025-07-06)

**Issue**: UseAPI.net support indicated we were using deprecated/non-existent endpoints
**Resolution**: Migrated from VEO2 to Pixverse v4 API

**Deprecated Endpoints (DO NOT USE):**
```
https://api.useapi.net/v1/veo2/generate
https://api.useapi.net/v1/veo2/status/{video_id}
https://api.useapi.net/v1/status  # This endpoint does NOT exist
```

**Current Endpoints (USE THESE):**
```
https://api.useapi.net/v2/pixverse/videos/create-v4
https://api.useapi.net/v2/pixverse/videos/{video_id}
```

**Important Notes**:
- The endpoint `/v1/status` does NOT exist. Use service-specific endpoints only
- Some services return 400 errors on incorrect endpoints rather than 404
- The Pixverse video creation endpoint is confirmed working
- Authentication works but many endpoints have strict URL requirements
- UseAPI.net support recommends checking https://useapi.net/docs/api-ltxstudio-v1 for correct endpoints

### 2. Redis to Cloud Tasks Migration (2025-07-07)

**Complete removal of Redis** in favor of Google Cloud Tasks:
- Queue Manager: Only supports Cloud Tasks (no Redis fallback)
- Worker: HTTP-based Cloud Tasks worker deployed to Cloud Run
- URL: https://tenxsom-video-worker-hpkm6siuqq-uc.a.run.app

## API Configurations

### UseAPI.net Configuration
- **Base URL**: `https://api.useapi.net/v1` (some services use v2)
- **Bearer Token**: `user:1831-r8vA1WGayarXKuYwpT1PW`
- **Primary Account**: goldensonproperties@gmail.com
- **Secondary Account**: tenxsom.ai.1@gmail.com

### Service Endpoints
```python
# From useapi_mcp_server/config.py
SERVICE_BASE_PATHS = {
    "ltxstudio": "/ltxstudio",
    "midjourney": "/midjourney", 
    "pixverse": "/pixverse",
    "minimax": "/minimax",
    "runway": "/runway",
    "kling": "/kling",
    "pika": "/pika",
    "mureka": "/mureka",
    "tempolor": "/tempolor",
    "insight_face_swap": "/insight-face-swap"
}
```

### Telegram Bot Configuration
- **Bot Token**: `8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8`
- **Bot Username**: @TenxsomAI_bot
- **Authorized User ID**: `8088003389`
- **Connection Method**: Polling (not webhook)

## Environment Variables Required

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
CLOUD_TASKS_WORKER_URL=https://tenxsom-video-worker-hpkm6siuqq-uc.a.run.app/process_video_job

# UseAPI.net
USEAPI_BEARER_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW
USEAPI_PRIMARY_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW
USEAPI_SECONDARY_1_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW

# Telegram
TELEGRAM_BOT_TOKEN=8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8
AUTHORIZED_USER_ID=8088003389

# YouTube API (not yet configured)
YOUTUBE_API_KEY=
YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=

# Google AI Ultra
GOOGLE_AI_ULTRA_CREDENTIALS=/path/to/credentials.json
```

## Known Issues and Workarounds

1. **UseAPI.net /v1/status endpoint doesn't exist**
   - Use service-specific endpoints instead
   - Check health via actual service calls

2. **Missing directories need creation**:
   ```bash
   mkdir -p monitoring/alerts flow_reports videos/output
   ```

3. **Google Cloud Tasks library import error**
   - Install: `pip install google-cloud-tasks`

4. **Worker URL defaults to localhost**
   - Set CLOUD_TASKS_WORKER_URL environment variable

## Architectural Decisions

### 1. AI-Powered Components (2025-07-07)
- **intelligent_topic_generator.py**: Replaces static production_topics.txt
- **intelligent_resource_optimizer.py**: Dynamic quota allocation
- **intelligent_monitoring_system.py**: ML-based anomaly detection

### 2. Platform Expert Agents
- YouTube Expert Agent for trend analysis
- Intelligent fallback mechanisms when experts fail
- Context-aware topic generation based on time/platform

### 3. Fail-over Mechanisms
- Multi-account UseAPI.net redundancy
- Polling-based Telegram bot (resilient to network issues)
- Google Cloud Tasks with 99.95% uptime SLA
- AI-powered adaptive fallbacks

## Testing Commands

### Test Endpoints
```bash
# Cloud Tasks Worker Health
curl https://tenxsom-video-worker-hpkm6siuqq-uc.a.run.app/health

# Telegram Bot
curl https://api.telegram.org/bot8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8/getMe
```

### Launch Production
```bash
# Single video
python3 tenxsom_flow_engine/run_flow.py single --topic "AI Innovation"

# Daily production
python3 tenxsom_flow_engine/run_flow.py schedule --daily-count 96

# Start Telegram bot
cd chatbot-integration && python3 central-controller.py
```

### Monitor System
```bash
# Check intelligent monitoring
python3 intelligent_monitoring_system.py --health

# View active alerts
python3 intelligent_monitoring_system.py --daemon
```

## Recent Changes (2025-07-07)

1. **Removed all mock functions and placeholders**
2. **Completely replaced Redis with Google Cloud Tasks**
3. **Integrated YouTube Platform Expert Agent throughout**
4. **Replaced all hardcoded elements with AI-powered systems**
5. **Deployed worker to Cloud Run**
6. **Verified endpoint connectivity (75% operational)**
7. **Removed all VEO2 references and updated to Pixverse v4**
8. **Replaced platform upload stubs with proper implementations**
9. **Updated hardcoded credentials to use environment variables**
10. **Implemented real notification system with Telegram/webhook/Discord integration**
11. **Removed test files from production deployment**

## Next Steps

1. Set missing environment variables (YouTube API, CLOUD_TASKS_WORKER_URL)
2. Create missing directories
3. Install google-cloud-tasks library
4. Configure YouTube API credentials for upload functionality
5. Consider setting up webhook for Telegram bot (currently using polling)