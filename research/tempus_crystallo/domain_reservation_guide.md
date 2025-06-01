# Domain Reservation and CloudFront Automation Setup Guide

## Step 1: Reserve tenxsom.ai Domain

### Option A: AWS Route 53 (Recommended for AWS Integration)
```bash
# Check domain availability
aws route53domains check-domain-availability --domain-name tenxsom.ai

# Register domain through Route 53
aws route53domains register-domain \
    --domain-name tenxsom.ai \
    --duration-in-years 1 \
    --admin-contact file://admin-contact.json \
    --registrant-contact file://registrant-contact.json \
    --tech-contact file://tech-contact.json \
    --privacy-protection-admin-contact \
    --privacy-protection-registrant-contact \
    --privacy-protection-tech-contact
```

**Contact JSON Template** (`admin-contact.json`):
```json
{
    "FirstName": "Your Name",
    "LastName": "Last Name", 
    "ContactType": "PERSON",
    "OrganizationName": "Tenxsom AI",
    "AddressLine1": "Your Address",
    "City": "Your City",
    "State": "Your State",
    "CountryCode": "US",
    "ZipCode": "Your Zip",
    "PhoneNumber": "+1.5551234567",
    "Email": "admin@tenxsom.ai"
}
```

### Option B: External Registrar + Route 53 Hosting
1. **Register at Namecheap/GoDaddy**: Quick reservation (~$15-30/year)
2. **Transfer DNS to Route 53**: For AWS integration benefits
3. **Update Nameservers**: Point to Route 53 hosted zone

## Step 2: AWS CloudFront Continuous Deployment Setup

### Architecture Overview
```
GitHub Repository → AWS CodePipeline → CodeBuild → CloudFront Distribution
     ↓                    ↓              ↓             ↓
Source Code      →    CI/CD Pipeline → Build Assets → Global CDN
```

### CloudFormation Template for Full Automation
```yaml
# cloudfront-cicd-template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Tenxsom AI CloudFront Continuous Deployment Pipeline'

Parameters:
  DomainName:
    Type: String
    Default: tenxsom.ai
    Description: Primary domain name
  
  GitHubRepo:
    Type: String
    Default: Tenxsom_AI/tenxsom-website
    Description: GitHub repository name
  
  GitHubToken:
    Type: String
    NoEcho: true
    Description: GitHub personal access token

Resources:
  # S3 Bucket for Website Content
  WebsiteBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${DomainName}-website-content'
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
      VersioningConfiguration:
        Status: Enabled

  # S3 Bucket Policy for CloudFront Access
  WebsiteBucketPolicy:
    Type: AWS::S3::BucketPolicy
    Properties:
      Bucket: !Ref WebsiteBucket
      PolicyDocument:
        Statement:
          - Sid: AllowCloudFrontServicePrincipal
            Effect: Allow
            Principal:
              Service: cloudfront.amazonaws.com
            Action: 's3:GetObject'
            Resource: !Sub '${WebsiteBucket}/*'
            Condition:
              StringEquals:
                'AWS:SourceArn': !Sub 'arn:aws:cloudfront::${AWS::AccountId}:distribution/*'

  # CloudFront Origin Access Control
  OriginAccessControl:
    Type: AWS::CloudFront::OriginAccessControl
    Properties:
      OriginAccessControlConfig:
        Name: !Sub '${DomainName}-OAC'
        OriginAccessControlOriginType: s3
        SigningBehavior: always
        SigningProtocol: sigv4

  # CloudFront Distribution
  CloudFrontDistribution:
    Type: AWS::CloudFront::Distribution
    Properties:
      DistributionConfig:
        Aliases:
          - !Ref DomainName
          - !Sub 'www.${DomainName}'
        DefaultCacheBehavior:
          TargetOriginId: S3Origin
          ViewerProtocolPolicy: redirect-to-https
          CachePolicyId: 4135ea2d-6df8-44a3-9df3-4b5a84be39ad  # CachingOptimized
          OriginRequestPolicyId: 88a5eaf4-2fd4-4709-b370-b4c650ea3fcf  # CORS-S3Origin
          ResponseHeadersPolicyId: 67f7725c-6f97-4210-82d7-5512b31e9d03  # SecurityHeaders
        Origins:
          - Id: S3Origin
            DomainName: !GetAtt WebsiteBucket.RegionalDomainName
            S3OriginConfig:
              OriginAccessIdentity: ''
            OriginAccessControlId: !Ref OriginAccessControl
        Enabled: true
        DefaultRootObject: index.html
        CustomErrorResponses:
          - ErrorCode: 404
            ResponseCode: 200
            ResponsePagePath: /index.html
          - ErrorCode: 403
            ResponseCode: 200
            ResponsePagePath: /index.html
        PriceClass: PriceClass_100
        ViewerCertificate:
          AcmCertificateArn: !Ref SSLCertificate
          SslSupportMethod: sni-only
          MinimumProtocolVersion: TLSv1.2_2021

  # SSL Certificate
  SSLCertificate:
    Type: AWS::CertificateManager::Certificate
    Properties:
      DomainName: !Ref DomainName
      SubjectAlternativeNames:
        - !Sub 'www.${DomainName}'
      ValidationMethod: DNS
      DomainValidationOptions:
        - DomainName: !Ref DomainName
          HostedZoneId: !Ref HostedZone

  # Route 53 Hosted Zone
  HostedZone:
    Type: AWS::Route53::HostedZone
    Properties:
      Name: !Ref DomainName

  # Route 53 Records
  DNSRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneId: !Ref HostedZone
      Name: !Ref DomainName
      Type: A
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        HostedZoneId: Z2FDTNDATAQYW2  # CloudFront Hosted Zone ID

  WWWDNSRecord:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneId: !Ref HostedZone
      Name: !Sub 'www.${DomainName}'
      Type: A
      AliasTarget:
        DNSName: !GetAtt CloudFrontDistribution.DomainName
        HostedZoneId: Z2FDTNDATAQYW2

  # CodeCommit Repository (Alternative to GitHub)
  CodeRepository:
    Type: AWS::CodeCommit::Repository
    Properties:
      RepositoryName: tenxsom-website
      RepositoryDescription: Tenxsom AI website repository

  # CodeBuild Project
  CodeBuildProject:
    Type: AWS::CodeBuild::Project
    Properties:
      Name: tenxsom-website-build
      ServiceRole: !GetAtt CodeBuildRole.Arn
      Artifacts:
        Type: CODEPIPELINE
      Environment:
        Type: LINUX_CONTAINER
        ComputeType: BUILD_GENERAL1_SMALL
        Image: aws/codebuild/standard:7.0
        EnvironmentVariables:
          - Name: S3_BUCKET
            Value: !Ref WebsiteBucket
          - Name: DISTRIBUTION_ID
            Value: !Ref CloudFrontDistribution
      Source:
        Type: CODEPIPELINE
        BuildSpec: |
          version: 0.2
          phases:
            pre_build:
              commands:
                - echo Logging in to Amazon ECR...
                - aws --version
            build:
              commands:
                - echo Build started on `date`
                - echo Building the website...
                # Add any build commands here (e.g., npm build, webpack, etc.)
            post_build:
              commands:
                - echo Build completed on `date`
                - echo Uploading to S3...
                - aws s3 sync . s3://$S3_BUCKET --delete
                - echo Invalidating CloudFront cache...
                - aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
          artifacts:
            files:
              - '**/*'

  # CodePipeline
  CodePipeline:
    Type: AWS::CodePipeline::Pipeline
    Properties:
      Name: tenxsom-website-pipeline
      RoleArn: !GetAtt CodePipelineRole.Arn
      ArtifactStore:
        Type: S3
        Location: !Ref ArtifactsBucket
      Stages:
        - Name: Source
          Actions:
            - Name: Source
              ActionTypeId:
                Category: Source
                Owner: ThirdParty
                Provider: GitHub
                Version: '1'
              Configuration:
                Owner: !Select [0, !Split ['/', !Ref GitHubRepo]]
                Repo: !Select [1, !Split ['/', !Ref GitHubRepo]]
                Branch: main
                OAuthToken: !Ref GitHubToken
              OutputArtifacts:
                - Name: SourceOutput
        - Name: Build
          Actions:
            - Name: Build
              ActionTypeId:
                Category: Build
                Owner: AWS
                Provider: CodeBuild
                Version: '1'
              Configuration:
                ProjectName: !Ref CodeBuildProject
              InputArtifacts:
                - Name: SourceOutput

  # IAM Roles
  CodeBuildRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: codebuild.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: CodeBuildPolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: '*'
              - Effect: Allow
                Action:
                  - s3:PutObject
                  - s3:PutObjectAcl
                  - s3:GetObject
                  - s3:DeleteObject
                Resource: !Sub '${WebsiteBucket}/*'
              - Effect: Allow
                Action:
                  - s3:ListBucket
                Resource: !Ref WebsiteBucket
              - Effect: Allow
                Action:
                  - cloudfront:CreateInvalidation
                Resource: '*'

  CodePipelineRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: codepipeline.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: CodePipelinePolicy
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                Resource: !Sub '${ArtifactsBucket}/*'
              - Effect: Allow
                Action:
                  - codebuild:BatchGetBuilds
                  - codebuild:StartBuild
                Resource: !GetAtt CodeBuildProject.Arn

  # Artifacts Bucket for CodePipeline
  ArtifactsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Sub '${DomainName}-pipeline-artifacts'
      VersioningConfiguration:
        Status: Enabled

Outputs:
  WebsiteURL:
    Description: Website URL
    Value: !Sub 'https://${DomainName}'
  
  CloudFrontDistributionId:
    Description: CloudFront Distribution ID
    Value: !Ref CloudFrontDistribution
  
  NameServers:
    Description: Route 53 Name Servers
    Value: !Join [', ', !GetAtt HostedZone.NameServers]
```

## Step 3: Deployment Commands

### Quick Deploy Script
```bash
#!/bin/bash
# deploy-tenxsom.sh

# Variables
DOMAIN_NAME="tenxsom.ai"
STACK_NAME="tenxsom-website-stack"
GITHUB_TOKEN="your_github_token_here"
GITHUB_REPO="your_username/tenxsom-website"

# Deploy CloudFormation stack
aws cloudformation deploy \
    --template-file cloudfront-cicd-template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        DomainName=$DOMAIN_NAME \
        GitHubRepo=$GITHUB_REPO \
        GitHubToken=$GITHUB_TOKEN \
    --capabilities CAPABILITY_IAM \
    --region us-east-1

# Get outputs
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs' \
    --output table
```

## Step 4: GitHub Repository Setup

### Create Repository Structure
```
tenxsom-website/
├── index.html (your website template)
├── css/
│   └── styles.css
├── js/
│   └── main.js
├── images/
│   └── logo.svg
├── buildspec.yml (CodeBuild configuration)
└── README.md
```

### BuildSpec.yml for Advanced Builds
```yaml
version: 0.2
phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws --version
      - echo Installing dependencies...
      # Add npm install, pip install, etc. if needed
  
  build:
    commands:
      - echo Build started on `date`
      - echo Building the Tenxsom AI website...
      # Add build commands:
      # - npm run build
      # - webpack --mode production
      # - python build.py
  
  post_build:
    commands:
      - echo Build completed on `date`
      - echo Uploading to S3...
      - aws s3 sync . s3://$S3_BUCKET --delete --exclude ".git/*" --exclude "node_modules/*"
      - echo Invalidating CloudFront cache...
      - aws cloudfront create-invalidation --distribution-id $DISTRIBUTION_ID --paths "/*"
      - echo Deployment complete!

artifacts:
  files:
    - '**/*'
  exclude-paths:
    - node_modules/**/*
    - .git/**/*
    - '*.md'
```

## Step 5: AI-Powered Automation Features

### CloudFront Continuous Deployment with AI
```yaml
# Enhanced with AWS AI services
ContinuousDeployment:
  Type: AWS::CloudFront::ContinuousDeployment
  Properties:
    ContinuousDeploymentPolicyConfig:
      Enabled: true
      StagingDistributionDnsNames:
        - staging.tenxsom.ai
      TrafficConfig:
        Type: SingleWeight
        SingleWeightConfig:
          Weight: 0.1  # 10% traffic to staging
          SessionStickinessConfig:
            IdleTTL: 300
            MaximumTTL: 600

# AI-powered monitoring
AIMonitoring:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: TenxsomAI-HighErrorRate
    ComparisonOperator: GreaterThanThreshold
    EvaluationPeriods: 2
    MetricName: ErrorRate
    Namespace: AWS/CloudFront
    Period: 300
    Statistic: Average
    Threshold: 5.0
    ActionsEnabled: true
    AlarmActions:
      - !Ref SNSRollbackTopic
```

## Expected Timeline and Costs

### Timeline
- **Domain Registration**: 15 minutes
- **CloudFormation Deployment**: 30-45 minutes (SSL cert validation)
- **DNS Propagation**: 24-48 hours (full global propagation)
- **Pipeline Setup**: 15 minutes
- **First Deployment**: 5-10 minutes

### Estimated Costs (Monthly)
- **Domain Registration**: $1-3/month (.ai domains ~$20-30/year)
- **Route 53 Hosted Zone**: $0.50/month
- **CloudFront**: $0.085/GB + $0.0075/10,000 requests
- **S3 Storage**: $0.023/GB/month
- **CodePipeline**: $1/pipeline/month
- **CodeBuild**: $0.005/build minute

**Total Expected**: $5-15/month for moderate traffic

## Next Steps

1. **Reserve Domain**: Execute domain registration immediately
2. **Prepare Repository**: Upload your website template to GitHub
3. **Deploy Stack**: Run CloudFormation deployment
4. **Test Pipeline**: Commit changes to trigger automatic deployment
5. **Monitor**: Use CloudWatch for performance tracking