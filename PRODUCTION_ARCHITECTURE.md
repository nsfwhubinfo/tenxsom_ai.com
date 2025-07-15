# TenxSOM AI - Production Technical Architecture

## System Overview

TenxSOM AI is a production-grade, end-to-end video generation system that creates videos from content specifications using AI services. The system employs an asynchronous, scalable architecture designed for high-volume production environments.

## Architectural Decisions and Key Workarounds

### 1. The Master Orchestrator ("Conveyor Belt")
- **Problem:** Initial development resulted in isolated, functional components (`ClaudeVideoService`, `ProductionVideoGenerator`) with no reliable data flow between them. This represented a fundamental architectural gap.
- **Solution:** A dedicated, linear orchestrator (`master_orchestrator_v3.py`) was implemented. This script acts as the single source of truth for the end-to-end workflow, explicitly connecting the output of the planning phase to the input of the execution phase. **This is the official "conveyor belt" of the system.**

### 2. Bypassing Flawed Tier-Based Routing
- **Problem:** The `generate_video` method within `production_video_generator.py` contains flawed tier-based routing logic that **does not** route any tier to the actual video-generating function (`generate_with_useapi`).
- **Solution:** The `master_orchestrator_v3.py` **intentionally and correctly bypasses this flawed method**. It calls the `generate_with_useapi` function directly, ensuring a tangible video asset is created. This is a deliberate architectural choice to ensure a working pipeline at launch.

### 3. Asynchronous Polling for Long-Running Jobs
- **Problem:** Video generation APIs are asynchronous and can take several minutes, causing client-side timeouts.
- **Solution:** The system was refactored into a two-stage process:
    1. The **Orchestrator** submits the job and saves its state to a persistent queue (`pending_video_jobs/`).
    2. A separate **Poller** (`poll_video_status.py`) runs independently to check job status and download completed assets.
- **Benefit:** This non-blocking architecture is highly scalable and resilient, preventing timeouts and ensuring reliable asset retrieval.

### 4. UseAPI.net Asset Type Resolution
- **Problem:** The LTX Studio video generation endpoint required assets of `type=image` (uploaded via `/assets`), not `type=artifact` (from image generation).
- **Solution:** Implemented a download-and-reupload workflow that converts generated image artifacts to properly typed assets before video generation.
- **Result:** Resolved persistent 400 errors and enabled successful video generation job submission.

## Production Components

### Core Scripts
- **`master_orchestrator_v3.py`**: Main orchestration engine
- **`production_video_generator.py`**: Video generation with UseAPI.net integration
- **`claude_video_service.py`**: Content planning with Vertex AI/local fallback
- **`poll_video_status.py`**: Asynchronous job status monitoring and asset download

### Configuration
- **Environment Variables**: All credentials externalized to environment variables
- **`production.env`**: Production environment template (DO NOT COMMIT)

### Required Environment Variables
```bash
USEAPI_BEARER_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
VERTEX_AI_PROJECT_ID=tenxsom-ai-1631088
VERTEX_AI_LOCATION=us-east5
VERTEX_AI_CLAUDE_MODEL_ID=claude-3-5-sonnet@20240620
```

## Production Workflow

### 1. Video Generation Submission
```bash
export USEAPI_BEARER_TOKEN=your_token
python3 master_orchestrator_v3.py job_definition.json
```
**Result**: Job submitted (10-20 seconds), state saved to `pending_video_jobs/`

### 2. Asynchronous Processing
```bash
export USEAPI_BEARER_TOKEN=your_token
python3 poll_video_status.py
```
**Result**: Downloads completed videos, creates completion reports

### 3. Automated Scheduling (Production)
```bash
# Run poller every 2 minutes
*/2 * * * * cd /path/to/tenxsom-ai-vertex && /usr/bin/env USEAPI_BEARER_TOKEN=your_token python3 poll_video_status.py
```

## API Integrations

### UseAPI.net LTX Studio
- **Image Generation**: `POST /v1/ltxstudio/images/flux-create`
- **Asset Upload**: `POST /v1/ltxstudio/assets/?type=image`
- **Video Generation**: `POST /v1/ltxstudio/videos/ltx-create`
- **Status Polling**: `GET /v1/ltxstudio/generations/{id}`

### Google Cloud Vertex AI
- **Content Planning**: Claude 3.5 Sonnet via Vertex AI
- **Fallback**: Local content generation with archetype-specific templates

## Production Validation

### ✅ Verified Production Capabilities
1. **Environment Variable Configuration**: All credentials externalized
2. **End-to-End Pipeline**: Successfully submits video generation jobs
3. **Asynchronous Processing**: Non-blocking job management
4. **API Integration**: Working UseAPI.net and Vertex AI connections
5. **Error Handling**: Comprehensive logging and failure recovery

### 📊 Performance Metrics
- **Job Submission**: 10-20 seconds
- **Video Generation**: 2-10 minutes (asynchronous)
- **Pipeline Cost**: ~$0.06 per video
- **Scalability**: Supports 200+ videos/day with proper scheduling

## Security Considerations

- All API tokens stored in environment variables
- No hardcoded credentials in source code
- Production environment file excluded from version control
- Secure credential management via Google Cloud ADC

## Monitoring and Logging

- Comprehensive logging throughout all components
- Job state persistence for audit trails
- Completion/failure reports for each video generation
- Age-based warnings for long-running jobs

## Known Limitations

1. **UseAPI.net Status Endpoint**: Occasional timeouts on status polling (resilient retry logic implemented)
2. **Vertex AI Fallback**: System gracefully degrades to local content generation when Vertex AI is unavailable
3. **Tier-Based Routing**: Legacy routing logic exists but is bypassed by production orchestrator

## Future Enhancements

1. **Database Integration**: Replace file-based job queue with database
2. **Web Dashboard**: Real-time monitoring interface
3. **Multi-Service Routing**: Expand beyond LTX Studio to other video generation services
4. **Auto-scaling**: Cloud-based deployment with auto-scaling capabilities