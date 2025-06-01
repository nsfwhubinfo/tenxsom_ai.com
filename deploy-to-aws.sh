#!/bin/bash

# Tenxsom AI Website Deployment Script
# Deploys website files to AWS S3

# Configuration
BUCKET_NAME="tenxsom-ai.com"
REGION="us-east-1"
CLOUDFRONT_DISTRIBUTION_ID="" # Add your CloudFront distribution ID here

echo "🚀 Deploying Tenxsom AI website to AWS S3..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   sudo apt install awscli"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run:"
    echo "   aws configure"
    exit 1
fi

# Navigate to website files directory
cd website-files || exit 1

# Sync files to S3
echo "📤 Uploading files to S3..."
aws s3 sync . s3://${BUCKET_NAME} \
    --exclude ".git/*" \
    --exclude "*.sh" \
    --exclude "*.md" \
    --exclude "bucket-policy.json" \
    --delete \
    --acl public-read

# Set proper content types
echo "🔧 Setting content types..."
aws s3 cp s3://${BUCKET_NAME} s3://${BUCKET_NAME} \
    --recursive \
    --exclude "*" \
    --include "*.html" \
    --content-type "text/html" \
    --metadata-directive REPLACE \
    --acl public-read

aws s3 cp s3://${BUCKET_NAME} s3://${BUCKET_NAME} \
    --recursive \
    --exclude "*" \
    --include "*.json" \
    --content-type "application/json" \
    --metadata-directive REPLACE \
    --acl public-read

aws s3 cp s3://${BUCKET_NAME} s3://${BUCKET_NAME} \
    --recursive \
    --exclude "*" \
    --include "*.css" \
    --content-type "text/css" \
    --metadata-directive REPLACE \
    --acl public-read

aws s3 cp s3://${BUCKET_NAME} s3://${BUCKET_NAME} \
    --recursive \
    --exclude "*" \
    --include "*.js" \
    --content-type "application/javascript" \
    --metadata-directive REPLACE \
    --acl public-read

# Set cache headers
echo "⚡ Setting cache headers..."
# HTML files - short cache
aws s3 cp s3://${BUCKET_NAME} s3://${BUCKET_NAME} \
    --recursive \
    --exclude "*" \
    --include "*.html" \
    --cache-control "max-age=3600" \
    --metadata-directive REPLACE \
    --acl public-read

# Static assets - longer cache
aws s3 cp s3://${BUCKET_NAME} s3://${BUCKET_NAME} \
    --recursive \
    --exclude "*.html" \
    --exclude "*.json" \
    --cache-control "max-age=86400" \
    --metadata-directive REPLACE \
    --acl public-read

# Invalidate CloudFront cache if distribution ID is set
if [ ! -z "$CLOUDFRONT_DISTRIBUTION_ID" ]; then
    echo "🔄 Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID \
        --paths "/*"
fi

echo "✅ Deployment complete!"
echo "🌐 Website URL: https://${BUCKET_NAME}"
echo ""
echo "📝 Next steps:"
echo "1. Ensure your Route 53 records point to your S3 bucket or CloudFront distribution"
echo "2. Set up CloudFront for HTTPS support if not already done"
echo "3. Configure the bucket policy using bucket-policy.json"