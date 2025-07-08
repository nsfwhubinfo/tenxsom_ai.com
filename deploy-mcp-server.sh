#!/bin/bash

# TenxsomAI MCP Server Deployment Script
# Deploys MCP server to Google Cloud Run with PostgreSQL database

set -e

# Configuration
PROJECT_ID=${1:-"tenxsom-ai-production"}
REGION=${2:-"us-central1"}
DB_INSTANCE_NAME="tenxsom-mcp-db"
SERVICE_NAME="tenxsom-mcp-server"

echo "🚀 Deploying TenxsomAI MCP Server"
echo "=================================="
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Database: $DB_INSTANCE_NAME"
echo "Service: $SERVICE_NAME"
echo ""

# Set project
echo "📋 Setting up Google Cloud project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create Cloud SQL PostgreSQL instance if it doesn't exist
echo "🗄️ Setting up PostgreSQL database..."
if ! gcloud sql instances describe $DB_INSTANCE_NAME --project=$PROJECT_ID >/dev/null 2>&1; then
    echo "Creating Cloud SQL instance: $DB_INSTANCE_NAME"
    gcloud sql instances create $DB_INSTANCE_NAME \
        --database-version=POSTGRES_15 \
        --cpu=1 \
        --memory=4GB \
        --region=$REGION \
        --storage-type=SSD \
        --storage-size=20GB \
        --storage-auto-increase \
        --backup-start-time=03:00 \
        --enable-bin-log \
        --deletion-protection
    
    echo "⏳ Waiting for database instance to be ready..."
    gcloud sql instances patch $DB_INSTANCE_NAME --no-deletion-protection
else
    echo "✅ Cloud SQL instance already exists: $DB_INSTANCE_NAME"
fi

# Create database and user
echo "👤 Setting up database and user..."
DB_PASSWORD=$(openssl rand -base64 32)

# Store database password in Secret Manager
echo "🔐 Storing database credentials in Secret Manager..."
echo -n "$DB_PASSWORD" | gcloud secrets create mcp-db-password --data-file=- --replication-policy=automatic || true

# Create database user
gcloud sql users create mcpuser \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD || echo "User might already exist"

# Create database
gcloud sql databases create tenxsom_mcp \
    --instance=$DB_INSTANCE_NAME || echo "Database might already exist"

# Grant permissions
gcloud sql users set-password mcpuser \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD

# Create database URL secret
DB_URL="postgresql://mcpuser:$DB_PASSWORD@/$DB_INSTANCE_NAME?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME&dbname=tenxsom_mcp"
echo -n "$DB_URL" | gcloud secrets create mcp-database-url --data-file=- --replication-policy=automatic || \
echo -n "$DB_URL" | gcloud secrets versions add mcp-database-url --data-file=-

# Store UseAPI token in Secret Manager
if [ ! -z "$USEAPI_BEARER_TOKEN" ]; then
    echo "🔑 Storing UseAPI token in Secret Manager..."
    echo -n "$USEAPI_BEARER_TOKEN" | gcloud secrets create useapi-bearer-token --data-file=- --replication-policy=automatic || \
    echo -n "$USEAPI_BEARER_TOKEN" | gcloud secrets versions add useapi-bearer-token --data-file=-
else
    echo "⚠️ USEAPI_BEARER_TOKEN not set. Please set it manually in Secret Manager."
fi

# Build and deploy using Cloud Build
echo "🏗️ Building and deploying MCP server..."
cd useapi-mcp-server

# Substitute PROJECT_ID in service.yaml
sed "s/PROJECT_ID/$PROJECT_ID/g" service.yaml > service-deployed.yaml

# Submit build
gcloud builds submit --config cloudbuild.yaml \
    --substitutions _PROJECT_ID=$PROJECT_ID \
    ..

# Get service URL
echo "🌐 Getting service URL..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo ""
echo "✅ Deployment complete!"
echo "======================="
echo "🔗 MCP Server URL: $SERVICE_URL"
echo "🗄️ Database Instance: $PROJECT_ID:$REGION:$DB_INSTANCE_NAME"
echo "📊 Cloud Console: https://console.cloud.google.com/run/detail/$REGION/$SERVICE_NAME/metrics?project=$PROJECT_ID"
echo ""
echo "🧪 Test the deployment:"
echo "curl $SERVICE_URL/health"
echo "curl $SERVICE_URL/api/status"
echo ""
echo "📋 Next steps:"
echo "1. Load MCP templates: python load_mcp_templates.py"
echo "2. Test end-to-end workflow"
echo "3. Configure monitoring and alerts"