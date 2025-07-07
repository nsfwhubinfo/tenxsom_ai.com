#!/bin/bash
# Script to remove Redis dependencies and migrate to Cloud Tasks

echo "🔄 Migrating from Redis to Google Cloud Tasks..."

# Backup current files
echo "📦 Creating backup..."
cp tenxsom_flow_engine/run_flow.py tenxsom_flow_engine/run_flow.py.redis_backup
cp tenxsom_flow_engine/worker.py tenxsom_flow_engine/worker.py.redis_backup

# Update run_flow.py to use enhanced version
echo "✏️ Updating run_flow.py..."
cp tenxsom_flow_engine/run_flow_enhanced.py tenxsom_flow_engine/run_flow.py

# Update imports in worker.py to remove Redis dependencies
echo "✏️ Updating worker.py..."
sed -i 's/import redis/#import redis # Replaced by Cloud Tasks/g' tenxsom_flow_engine/worker.py
sed -i 's/from redis import Redis/#from redis import Redis # Replaced by Cloud Tasks/g' tenxsom_flow_engine/worker.py

# Create environment configuration
echo "📝 Creating environment configuration..."
cat > .env.production << 'EOF'
# Google Cloud Tasks Configuration
export GOOGLE_APPLICATION_CREDENTIALS=/home/golde/.google-ai-ultra-credentials.json
export TENXSOM_QUEUE_TYPE=cloud_tasks
export CLOUD_TASKS_WORKER_URL=https://your-production-worker-url/process_video_job
export GOOGLE_CLOUD_PROJECT=tenxsom-ai-1631088
EOF

echo "✅ Migration complete!"
echo ""
echo "Next steps:"
echo "1. Deploy the worker to a public endpoint (see CLOUD_TASKS_DEPLOYMENT_GUIDE.md)"
echo "2. Update CLOUD_TASKS_WORKER_URL in .env.production with your worker URL"
echo "3. Source the environment: source .env.production"
echo "4. Test with: python3 run_flow.py --queue-type cloud_tasks single --topic 'Test'"
echo ""
echo "📚 Redis backup files created:"
echo "   - tenxsom_flow_engine/run_flow.py.redis_backup"
echo "   - tenxsom_flow_engine/worker.py.redis_backup"