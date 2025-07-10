#!/bin/bash
# Quick deployment script for TenxsomAI components

echo "🚀 TenxsomAI Quick Deployment Script"
echo "====================================="

# Set project
gcloud config set project tenxsom-ai-1631088

# Build and push content-pipeline
echo "📦 Building content-pipeline..."
docker build -t gcr.io/tenxsom-ai-1631088/content-pipeline:latest -f Dockerfile.content-pipeline .
docker push gcr.io/tenxsom-ai-1631088/content-pipeline:latest

# Deploy content-pipeline to us-central1
echo "🚀 Deploying content-pipeline to us-central1..."
gcloud run deploy content-pipeline \
  --image gcr.io/tenxsom-ai-1631088/content-pipeline:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=tenxsom-ai-1631088 \
  --service-account content-pipeline-manager@tenxsom-ai-1631088.iam.gserviceaccount.com

# Build and push platform-agents
echo "📦 Building platform-agents..."
docker build -t gcr.io/tenxsom-ai-1631088/platform-agents:latest -f Dockerfile.platform-agents .
docker push gcr.io/tenxsom-ai-1631088/platform-agents:latest

# Deploy platform-agents to us-central1
echo "🚀 Deploying platform-agents to us-central1..."
gcloud run deploy platform-agents \
  --image gcr.io/tenxsom-ai-1631088/platform-agents:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 5 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=tenxsom-ai-1631088 \
  --service-account platform-agents-manager@tenxsom-ai-1631088.iam.gserviceaccount.com

echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. Test the services using their health endpoints"
echo "2. Configure global load balancer if needed"
echo "3. Set up monitoring dashboards"
echo ""
echo "🔗 Service URLs:"
gcloud run services list --platform managed --region us-central1 --filter="metadata.name:content-pipeline OR metadata.name:platform-agents" --format="table(metadata.name,status.url)"