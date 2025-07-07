# Tenxsom AI Production System

Complete production-ready AI content generation and monetization system for automated YouTube, TikTok, Instagram, and X content creation.

## 🚀 Quick Start

**One-command startup:**
```bash
./quick_start.sh start
```

**Check system status:**
```bash
./quick_start.sh status
```

**Stop system:**
```bash
./quick_start.sh stop
```

## 📋 System Overview

Tenxsom AI is a comprehensive content automation system designed for aggressive 30-day YouTube monetization:

- **Daily Target**: 96 videos per day (4 premium, 8 standard, 84 volume)
- **Monthly Cost**: ~$80 (Google AI Ultra + UseAPI.net accounts)
- **Revenue Model**: YouTube Partner Program monetization
- **Multi-Platform**: YouTube (80%), TikTok (10%), Instagram (5%), X (5%)

## 🏗️ Architecture

### Core Components

1. **Production Deployment Manager** (`production_deployment.py`)
   - 7-phase automated deployment
   - Health monitoring and backup systems
   - Service orchestration and recovery

2. **Monetization Strategy Executor** (`monetization_strategy_executor.py`)
   - Three-tier content generation (Veo3 Quality, Veo3 Fast, LTX Turbo)
   - Optimal cost distribution and quota management
   - Google AI Ultra integration for premium content

3. **Daily Content Scheduler** (`daily_content_scheduler.py`)
   - 5 daily execution windows (06:00, 10:00, 14:00, 18:00, 22:00)
   - Resource-aware batch processing
   - Automated retry and error handling

4. **Content Upload Orchestrator** (`content_upload_orchestrator.py`)
   - Multi-platform upload automation
   - Smart quota management and rate limiting
   - A/B testing for thumbnails and metadata

5. **Analytics Tracker** (`analytics_tracker.py`)
   - YouTube Partner Program progress monitoring
   - ROI analysis and monetization tracking
   - Performance insights and recommendations

### Supporting Services

- **Enhanced Model Router** (`enhanced-model-router.py`) - Three-tier generation routing
- **UseAPI.net MCP Server** (`useapi-mcp-server/`) - 25+ tools for external services
- **Telegram Bot Integration** (`chatbot-integration/`) - Mobile system control
- **YouTube Upload Pipeline** (`youtube-upload-pipeline/`) - OAuth 2.0 + Analytics API
- **System Monitor** (`system_monitor.py`) - Real-time performance monitoring

## 🔧 Installation & Setup

### Prerequisites

- Python 3.8+
- Google Cloud Project with YouTube Data API v3
- UseAPI.net account with bearer token
- Telegram Bot Token (optional)
- 16GB+ RAM recommended for production

### Environment Configuration

Create `.env` file with required credentials:

```bash
# UseAPI.net Configuration
USEAPI_BEARER_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW

# YouTube API Configuration  
YOUTUBE_API_KEY=AIzaSyC3zuRXZc06A6EGBgL8yxnrNQlzuMN1eAg
YOUTUBE_CHANNEL_ID=UCHTnKvKvQiglq2_yaOcQiFg

# Google AI Ultra Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-ai-ultra-credentials.json

# Telegram Bot (Optional)
TELEGRAM_BOT_TOKEN=8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8
TELEGRAM_USER_ID=8088003389

# MCP Configuration
MCP_SERVER_NAME=useapi-net
MCP_SERVER_VERSION=1.0.0
```

### Google AI Ultra Setup

1. Create Google Cloud Project
2. Enable Vertex AI API
3. Create service account with Vertex AI permissions
4. Download credentials JSON file
5. Set `GOOGLE_APPLICATION_CREDENTIALS` path

### YouTube API Setup

1. Create Google Cloud Project (or use existing)
2. Enable YouTube Data API v3
3. Create API key and OAuth 2.0 credentials
4. Configure OAuth consent screen
5. Add authorized redirect URIs

## 🎯 Production Deployment

### Automated Deployment

```bash
# Full production deployment
python production_deployment.py

# Or use quick start
./quick_start.sh deploy
```

### Manual Deployment Steps

1. **Environment Validation**
   ```bash
   python production_config_manager.py
   ```

2. **Service Testing**
   ```bash
   python end_to_end_pipeline_test.py
   ```

3. **Production Startup**
   ```bash
   python production_startup.py start
   ```

### Deployment Phases

1. **Validation** - Environment and configuration checks
2. **Core Services** - Initialize main system components  
3. **Monitoring** - Start health checks and performance tracking
4. **Automation** - Deploy MCP server and Telegram integration
5. **Content Pipeline** - Enable content generation workflow
6. **Production Monitoring** - Real-time dashboard and alerting
7. **Finalization** - Generate reports and enable full automation

## 📊 System Management

### Status Monitoring

```bash
# System status
./quick_start.sh status

# Health check
./quick_start.sh health

# View logs
./quick_start.sh logs

# System metrics
python system_monitor.py
```

### Service Management

```bash
# Restart system
./quick_start.sh restart

# Start without optional services
./quick_start.sh start --no-optional

# Run system test
./quick_start.sh test
```

### Production Directories

- `production/logs/` - System and service logs
- `production/backups/` - Automated system backups (every 6 hours)
- `production/monitoring/` - Performance metrics and health reports
- `production/reports/` - Daily analytics and deployment reports
- `production/startup/` - Startup and management logs

## 📈 Monetization Strategy

### 30-Day Timeline

**Week 1-2: Foundation Building**
- Launch daily content generation (96 videos/day)
- Establish YouTube channel branding and optimization
- Build initial subscriber base and watch time

**Week 3-4: Growth Acceleration**
- Optimize content based on analytics insights
- Scale successful content formats
- A/B test thumbnails and titles for maximum CTR

**Monetization Requirements:**
- 1,000 subscribers
- 4,000 watch hours (past 12 months)
- Compliance with YouTube Partner Program policies

### Cost Optimization

- **Premium Content (4/day)**: Veo3 Quality - $0.85/video
- **Standard Content (8/day)**: Veo3 Fast - $0.20/video  
- **Volume Content (84/day)**: LTX Turbo - $0.00/video
- **Average Cost**: $0.028/video
- **Monthly Budget**: ~$80

## 🔧 API Integrations

### UseAPI.net Services

- **Midjourney**: Image generation for thumbnails
- **LTX Studio**: Free video generation (LTX Turbo)
- **Veo2**: High-quality video generation
- **HeyGen**: TTS with 1,500+ voices
- **Discord Monitoring**: Automated service detection

### Google Services

- **Vertex AI**: Veo3 video generation (Google AI Ultra plan)
- **YouTube Data API v3**: Video uploads and analytics
- **YouTube Analytics API**: Performance tracking
- **Cloud Storage**: Asset and backup storage

### Social Platforms

- **YouTube**: Primary monetization platform (80% content)
- **TikTok**: Viral content distribution (10% content)
- **Instagram**: Visual content sharing (5% content)
- **X (Twitter)**: Community engagement (5% content)

## 🛠️ Development & Testing

### Running Tests

```bash
# End-to-end pipeline test
python end_to_end_pipeline_test.py

# Individual component tests
python analytics_tracker.py
python content_upload_orchestrator.py
python monetization_strategy_executor.py
```

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run in development mode
python production_startup.py start --no-optional
```

### MCP Server Development

```bash
# Test MCP server
cd useapi-mcp-server
python -m src.useapi_mcp_server.server

# Install for Claude integration
pip install -e .
```

## 📋 Troubleshooting

### Common Issues

**Environment Variables**
```bash
# Check missing variables
python production_config_manager.py
```

**Service Failures**
```bash
# Check service logs
tail -f production/logs/service_*.log

# Restart specific service
python production_startup.py restart
```

**API Quota Issues**
```bash
# Check quota usage
./quick_start.sh status

# View quota tracking
python content_upload_orchestrator.py
```

### System Recovery

**Automated Recovery**
- Services auto-restart on failure
- Backup system runs every 6 hours
- Health checks every 5 minutes

**Manual Recovery**
```bash
# Restore from backup
cp -r production/backups/backup_latest/* .

# Reset system state
./quick_start.sh stop
./quick_start.sh start
```

## 📞 Support & Documentation

### Key Documentation

- `video-generation-success.md` - Video generation troubleshooting
- `monetization_strategy_executor.py` - Cost optimization details
- `analytics_tracker.py` - Monetization progress tracking
- `production_deployment.py` - Deployment configuration

### Performance Monitoring

- Real-time dashboard: `production/monitoring/dashboard.json`
- Daily reports: `production/reports/`
- System metrics: `python system_monitor.py`

### Getting Help

1. Check system logs: `./quick_start.sh logs`
2. Run health check: `./quick_start.sh health`
3. Review configuration: `python production_config_manager.py`
4. Run system test: `./quick_start.sh test`

---

## 🎯 Ready for Production

The Tenxsom AI system is designed for fully automated 30-day YouTube monetization. Once deployed, it requires minimal intervention while generating consistent, high-quality content across multiple platforms.

**Start your monetization journey:**
```bash
./quick_start.sh start
```

🚀 **System ready for aggressive content automation and YouTube monetization!**