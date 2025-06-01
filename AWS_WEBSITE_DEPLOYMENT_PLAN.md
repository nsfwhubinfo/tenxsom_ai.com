# AWS Website Deployment Plan for tenxsom-ai.com

## Domain Configuration Summary
- **Domain**: tenxsom-ai.com (registered with AWS Route 53)
- **Purpose**: Public-facing marketing website for Tenxsom AI
- **Architecture**: Static website with API backend

## AWS Services Architecture

### 1. S3 Buckets Setup

#### Primary Website Bucket
```bash
# Create public website bucket
aws s3 mb s3://tenxsom-ai.com --region us-east-1

# Enable static website hosting
aws s3 website s3://tenxsom-ai.com \
  --index-document index.html \
  --error-document error.html

# Set bucket policy for public read
aws s3api put-bucket-policy --bucket tenxsom-ai.com \
  --policy file://bucket-policy.json
```

#### WWW Redirect Bucket
```bash
# Create www redirect bucket
aws s3 mb s3://www.tenxsom-ai.com --region us-east-1

# Configure redirect
aws s3api put-bucket-website --bucket www.tenxsom-ai.com \
  --website-configuration '{
    "RedirectAllRequestsTo": {
      "HostName": "tenxsom-ai.com",
      "Protocol": "https"
    }
  }'
```

### 2. CloudFront Distribution

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json
```

CloudFront configuration includes:
- SSL/TLS certificate for tenxsom-ai.com
- S3 bucket as origin
- Caching optimization
- HTTPS redirect

### 3. Route 53 Configuration

```bash
# Create A record for root domain
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "tenxsom-ai.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "Z2FDTNDATAQYW2",
          "DNSName": "d1234567890.cloudfront.net",
          "EvaluateTargetHealth": false
        }
      }
    }]
  }'

# Create CNAME for www
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "www.tenxsom-ai.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "tenxsom-ai.com"}]
      }
    }]
  }'
```

## Website Structure

```
tenxsom-ai.com/
├── index.html          # Main landing page
├── products/
│   └── iscan-life/     # iScan Life product page
├── api/
│   └── content-manifest.json  # Dynamic content
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── error.html         # 404 page
```

## Deployment Process

### 1. Prepare Website Files
```bash
cd /home/golde/Tenxsom_AI/website-files

# Ensure proper structure
mkdir -p assets/{css,js,images}
mkdir -p products/iscan-life
```

### 2. Create Main Landing Page
Update index.html with professional marketing content

### 3. Sync to S3
```bash
# Sync website files to S3
aws s3 sync . s3://tenxsom-ai.com \
  --exclude ".git/*" \
  --exclude "*.md" \
  --acl public-read

# Set cache headers
aws s3 cp s3://tenxsom-ai.com s3://tenxsom-ai.com \
  --recursive \
  --metadata-directive REPLACE \
  --cache-control "max-age=86400" \
  --exclude "*.html" 

# HTML files with shorter cache
aws s3 cp s3://tenxsom-ai.com s3://tenxsom-ai.com \
  --recursive \
  --metadata-directive REPLACE \
  --cache-control "max-age=3600" \
  --exclude "*" \
  --include "*.html"
```

### 4. CloudFront Invalidation
```bash
# Invalidate CloudFront cache after updates
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"
```

## Security Configuration

### S3 Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::tenxsom-ai.com/*"
    }
  ]
}
```

### CORS Configuration (if needed for API)
```json
{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedOrigins": ["https://tenxsom-ai.com"],
      "ExposeHeaders": [],
      "MaxAgeSeconds": 3600
    }
  ]
}
```

## Monitoring & Analytics

1. **CloudWatch**: Monitor S3 and CloudFront metrics
2. **AWS WAF**: Protect against common web exploits
3. **CloudFront Logs**: Analyze visitor patterns

## Cost Optimization

- Use S3 Intelligent-Tiering for automatic cost optimization
- CloudFront caching reduces S3 request costs
- Consider Reserved Capacity for predictable traffic

## Next Steps

1. Verify Route 53 hosted zone ID
2. Request SSL certificate in ACM (AWS Certificate Manager)
3. Create professional website content
4. Set up CI/CD pipeline for automated deployments
5. Configure monitoring and alerts

## Estimated Monthly Costs
- Route 53: $0.50 (hosted zone) + $0.40 (queries)
- S3: ~$0.023/GB storage + request costs
- CloudFront: ~$0.085/GB transfer (first 10TB)
- Total: ~$5-20/month for moderate traffic