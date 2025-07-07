#!/bin/bash

# Deploy Tenxsom AI to Google Cloud Run via Cloud Build

echo "🚀 Deploying Tenxsom AI with Vertex AI to Google Cloud..."

# Check if gcloud is configured
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install Google Cloud SDK."
    exit 1
fi

# Set project
gcloud config set project gen-lang-client-0874689591

# Deploy to Cloud Run
gcloud run deploy tenxsom-ai-vertex \
    --source . \
    --region us-east5 \
    --allow-unauthenticated \
    --service-account=tenxsom-ai-vertex@gen-lang-client-0874689591.iam.gserviceaccount.com \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=gen-lang-client-0874689591" \
    --memory=2Gi \
    --cpu=1 \
    --min-instances=1 \
    --max-instances=100

echo "✅ Deployment complete!"

# Get the URL
URL=$(gcloud run services describe tenxsom-ai-vertex --region us-east5 --format 'value(status.url)')
echo "🌐 Your app is live at: $URL"