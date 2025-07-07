# 🚀 Google Cloud Tasks Production Deployment Guide

## ✅ Migration Status: READY FOR PRODUCTION

The Google Cloud Tasks implementation is complete and tested. This guide shows how to deploy to production.

## 📊 Current Status

### ✅ Completed
- Cloud Tasks queue created: `tenxsom-video-generation`
- Worker service implemented and running locally
- Job submission working successfully
- Rate limiting configured (10 req/s, 5 concurrent)
- Retry policies configured (exponential backoff)
- All dependencies installed in virtual environment

### 🎯 Next Steps for Production

## Option 1: Deploy to Google Cloud Run (Recommended)

```bash
# 1. Create Dockerfile for the worker
cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY tenxsom_flow_engine/ ./tenxsom_flow_engine/

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the worker
CMD ["python", "-m", "tenxsom_flow_engine.cloud_tasks_worker", "--host", "0.0.0.0", "--port", "8080"]
EOF

# 2. Create requirements.txt
cat > requirements.txt << 'EOF'
google-cloud-tasks==2.19.3
flask==3.1.1
redis==6.2.0
aiohttp==3.12.13
EOF

# 3. Build and deploy to Cloud Run
gcloud run deploy tenxsom-video-worker \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 900 \
  --max-instances 10 \
  --service-account content-pipeline-manager@tenxsom-ai-1631088.iam.gserviceaccount.com

# 4. Get the Cloud Run URL
WORKER_URL=$(gcloud run services describe tenxsom-video-worker --region us-central1 --format 'value(status.url)')

# 5. Update Cloud Tasks to use the Cloud Run URL
export CLOUD_TASKS_WORKER_URL="${WORKER_URL}/process_video_job"
```

## Option 2: Deploy to Compute Engine

```bash
# 1. Create a startup script
cat > startup-script.sh << 'EOF'
#!/bin/bash
# Install dependencies
apt-get update
apt-get install -y python3-pip python3-venv git

# Clone repository
cd /opt
git clone https://github.com/your-repo/tenxsom-ai-vertex.git
cd tenxsom-ai-vertex

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install google-cloud-tasks flask redis aiohttp

# Start worker service
export GOOGLE_APPLICATION_CREDENTIALS=/opt/credentials.json
nohup python3 tenxsom_flow_engine/cloud_tasks_worker.py --host 0.0.0.0 --port 8080 &
EOF

# 2. Create VM instance
gcloud compute instances create tenxsom-video-worker \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --metadata-from-file startup-script=startup-script.sh \
  --service-account=content-pipeline-manager@tenxsom-ai-1631088.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --tags=http-server

# 3. Allow HTTP traffic
gcloud compute firewall-rules create allow-video-worker \
  --allow tcp:8080 \
  --source-ranges 0.0.0.0/0 \
  --target-tags http-server
```

## Option 3: Local Testing with ngrok (Development)

```bash
# 1. Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar xvzf ngrok-v3-stable-linux-amd64.tgz

# 2. Start the worker
source venv/bin/activate
python3 tenxsom_flow_engine/cloud_tasks_worker.py --host 0.0.0.0 --port 8080 &

# 3. Expose via ngrok
./ngrok http 8080

# 4. Use the ngrok URL for Cloud Tasks
export CLOUD_TASKS_WORKER_URL="https://your-ngrok-url.ngrok.io/process_video_job"
```

## 🔧 Production Configuration

### Environment Variables
```bash
# Required
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
export CLOUD_TASKS_WORKER_URL=https://your-worker-url.com/process_video_job

# Optional
export TENXSOM_QUEUE_TYPE=cloud_tasks  # Force Cloud Tasks
export GOOGLE_CLOUD_PROJECT=tenxsom-ai-1631088
```

### Security Considerations
1. **Authentication**: For production, secure the worker endpoint:
   ```python
   # In cloud_tasks_worker.py, add authentication
   from google.auth import verify_id_token
   
   @app.before_request
   def verify_cloud_tasks_request():
       if request.path == '/process_video_job':
           token = request.headers.get('Authorization', '').replace('Bearer ', '')
           # Verify the token is from Cloud Tasks
   ```

2. **Rate Limiting**: Already configured in queue settings
3. **Monitoring**: Enable Cloud Logging and Monitoring

## 📈 Testing Production Deployment

```bash
# 1. Set production worker URL
export CLOUD_TASKS_WORKER_URL=https://your-production-url/process_video_job

# 2. Test single video generation
python3 run_flow_enhanced.py --queue-type cloud_tasks single --topic "Production Test"

# 3. Test batch processing
python3 run_flow_enhanced.py --queue-type cloud_tasks batch --topics-file topics.txt

# 4. Schedule daily production (96 videos/day)
python3 run_flow_enhanced.py --queue-type cloud_tasks schedule --daily-count 96
```

## 🎯 Complete Migration Checklist

- [x] Cloud Tasks API enabled
- [x] Queue created with rate limiting
- [x] Worker service implemented
- [x] Permissions configured
- [x] Local testing successful
- [ ] Worker deployed to production endpoint
- [ ] Production URL configured
- [ ] End-to-end testing completed
- [ ] Redis instances decommissioned

## 💡 Benefits Over Redis

1. **No Infrastructure**: Serverless, no Redis instances to manage
2. **Built-in Retry**: Automatic exponential backoff
3. **Rate Limiting**: Native 10 req/s limit for API quotas
4. **Scheduling**: Built-in delayed execution
5. **Cost**: $0.40/million operations vs $50-200/month Redis
6. **Reliability**: Persistent queue, survives restarts

## 🚀 Ready for Production!

Once the worker is deployed to a public endpoint (Cloud Run recommended), the system will be fully operational with Google Cloud Tasks handling all video generation jobs with automatic retry, rate limiting, and monitoring.