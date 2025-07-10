#!/usr/bin/env python3
"""
Deploy TenxsomAI components to Google Cloud
Handles containerization, pushing to registry, and deployment
"""

import subprocess
import os
import sys
import json
import time
from datetime import datetime
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CloudDeployment:
    """Manage cloud deployment of TenxsomAI components"""
    
    def __init__(self, project_id="tenxsom-ai-1631088"):
        self.project_id = project_id
        self.region_primary = "us-central1"
        self.region_secondary = "us-east1"
        
        # Component configurations
        self.components = {
            "content-pipeline": {
                "dockerfile": "Dockerfile.content-pipeline",
                "service_name": "content-pipeline",
                "memory": "2Gi",
                "cpu": "2",
                "min_instances": {"primary": 1, "secondary": 0},
                "max_instances": {"primary": 10, "secondary": 5}
            },
            "platform-agents": {
                "dockerfile": "Dockerfile.platform-agents",
                "service_name": "platform-agents",
                "memory": "1Gi",
                "cpu": "1",
                "min_instances": {"primary": 0, "secondary": 0},
                "max_instances": {"primary": 5, "secondary": 3}
            }
        }
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        logger.info("🔍 Checking prerequisites...")
        
        # Check gcloud CLI
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True
            )
            current_project = result.stdout.strip()
            if current_project != self.project_id:
                logger.warning(f"Current project is {current_project}, expected {self.project_id}")
                logger.info(f"Setting project to {self.project_id}")
                subprocess.run(["gcloud", "config", "set", "project", self.project_id])
        except Exception as e:
            logger.error(f"❌ gcloud CLI not found or not configured: {e}")
            return False
        
        # Check Docker
        try:
            subprocess.run(["docker", "--version"], check=True, capture_output=True)
            logger.info("✅ Docker is installed")
        except:
            logger.error("❌ Docker not found. Please install Docker.")
            return False
        
        # Check required files
        required_files = [
            "Dockerfile.content-pipeline",
            "Dockerfile.platform-agents",
            "content_pipeline_server.py",
            "platform_agents_server.py",
            "requirements.txt"
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                logger.error(f"❌ Missing required file: {file}")
                return False
        
        logger.info("✅ All prerequisites met")
        return True
    
    def configure_docker_auth(self):
        """Configure Docker authentication for Google Container Registry"""
        logger.info("🔐 Configuring Docker authentication...")
        try:
            subprocess.run(
                ["gcloud", "auth", "configure-docker"],
                check=True
            )
            logger.info("✅ Docker authentication configured")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to configure Docker auth: {e}")
            return False
    
    def build_container(self, component_name):
        """Build Docker container for component"""
        logger.info(f"🔨 Building container: {component_name}")
        
        config = self.components[component_name]
        image_name = f"gcr.io/{self.project_id}/{component_name}"
        
        try:
            # Build with latest tag
            subprocess.run(
                [
                    "docker", "build",
                    "-t", f"{image_name}:latest",
                    "-t", f"{image_name}:{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "-f", config["dockerfile"],
                    "."
                ],
                check=True
            )
            logger.info(f"✅ Container built: {component_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to build {component_name}: {e}")
            return False
    
    def push_container(self, component_name):
        """Push container to Google Container Registry"""
        logger.info(f"📤 Pushing container: {component_name}")
        
        image_name = f"gcr.io/{self.project_id}/{component_name}"
        
        try:
            # Push all tags
            subprocess.run(
                ["docker", "push", "--all-tags", image_name],
                check=True
            )
            logger.info(f"✅ Container pushed: {component_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to push {component_name}: {e}")
            return False
    
    def deploy_to_cloud_run(self, component_name, region):
        """Deploy component to Cloud Run"""
        logger.info(f"🚀 Deploying {component_name} to {region}")
        
        config = self.components[component_name]
        image_name = f"gcr.io/{self.project_id}/{component_name}:latest"
        
        # Determine instance configuration based on region
        min_instances = config["min_instances"]["primary" if region == self.region_primary else "secondary"]
        max_instances = config["max_instances"]["primary" if region == self.region_primary else "secondary"]
        
        deploy_cmd = [
            "gcloud", "run", "deploy", config["service_name"],
            "--image", image_name,
            "--region", region,
            "--platform", "managed",
            "--allow-unauthenticated",
            "--memory", config["memory"],
            "--cpu", config["cpu"],
            "--timeout", "900",
            "--min-instances", str(min_instances),
            "--max-instances", str(max_instances),
            "--set-env-vars", f"GOOGLE_CLOUD_PROJECT={self.project_id}",
            "--service-account", f"{component_name}-manager@{self.project_id}.iam.gserviceaccount.com"
        ]
        
        # Add secrets for content-pipeline
        if component_name == "content-pipeline":
            deploy_cmd.extend([
                "--set-secrets", "USEAPI_BEARER_TOKEN=useapi-bearer-token:latest",
                "--set-secrets", "YOUTUBE_REFRESH_TOKEN=youtube-refresh-token-hub:latest"
            ])
        
        try:
            result = subprocess.run(deploy_cmd, check=True, capture_output=True, text=True)
            
            # Extract service URL
            for line in result.stdout.split('\n'):
                if "Service URL:" in line:
                    service_url = line.split("Service URL:")[1].strip()
                    logger.info(f"✅ Deployed to {region}: {service_url}")
                    return service_url
            
            logger.info(f"✅ Deployed {component_name} to {region}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to deploy {component_name} to {region}: {e}")
            return False
    
    def create_service_accounts(self):
        """Create service accounts if they don't exist"""
        logger.info("👤 Creating service accounts...")
        
        service_accounts = [
            ("content-pipeline-manager", "Content Pipeline Manager"),
            ("platform-agents-manager", "Platform Agents Manager")
        ]
        
        for sa_name, description in service_accounts:
            sa_email = f"{sa_name}@{self.project_id}.iam.gserviceaccount.com"
            
            # Check if service account exists
            check_cmd = ["gcloud", "iam", "service-accounts", "describe", sa_email]
            result = subprocess.run(check_cmd, capture_output=True)
            
            if result.returncode != 0:
                # Create service account
                create_cmd = [
                    "gcloud", "iam", "service-accounts", "create", sa_name,
                    "--display-name", description
                ]
                try:
                    subprocess.run(create_cmd, check=True)
                    logger.info(f"✅ Created service account: {sa_name}")
                    
                    # Grant necessary permissions
                    roles = [
                        "roles/storage.objectAdmin",
                        "roles/cloudtasks.enqueuer",
                        "roles/cloudsql.client",
                        "roles/logging.logWriter",
                        "roles/monitoring.metricWriter"
                    ]
                    
                    for role in roles:
                        grant_cmd = [
                            "gcloud", "projects", "add-iam-policy-binding", self.project_id,
                            "--member", f"serviceAccount:{sa_email}",
                            "--role", role
                        ]
                        subprocess.run(grant_cmd, check=True)
                    
                    logger.info(f"✅ Granted permissions to {sa_name}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to create service account {sa_name}: {e}")
            else:
                logger.info(f"✓ Service account already exists: {sa_name}")
    
    def run_cloud_build(self):
        """Run Cloud Build pipeline"""
        logger.info("🏗️ Running Cloud Build pipeline...")
        
        if not os.path.exists("cloudbuild-pipeline.yaml"):
            logger.error("❌ cloudbuild-pipeline.yaml not found")
            return False
        
        try:
            subprocess.run(
                ["gcloud", "builds", "submit", "--config", "cloudbuild-pipeline.yaml"],
                check=True
            )
            logger.info("✅ Cloud Build completed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Cloud Build failed: {e}")
            return False
    
    def deploy_all_components(self):
        """Deploy all components to cloud"""
        logger.info("🚀 Starting full cloud deployment")
        logger.info("=" * 60)
        
        # Check prerequisites
        if not self.check_prerequisites():
            logger.error("❌ Prerequisites check failed")
            return False
        
        # Configure Docker auth
        if not self.configure_docker_auth():
            return False
        
        # Create service accounts
        self.create_service_accounts()
        
        # Deploy each component
        deployment_results = {}
        
        for component_name in self.components:
            logger.info(f"\n📦 Processing component: {component_name}")
            
            # Build container
            if not self.build_container(component_name):
                deployment_results[component_name] = {"status": "failed", "step": "build"}
                continue
            
            # Push to registry
            if not self.push_container(component_name):
                deployment_results[component_name] = {"status": "failed", "step": "push"}
                continue
            
            # Deploy to primary region
            primary_url = self.deploy_to_cloud_run(component_name, self.region_primary)
            if not primary_url:
                deployment_results[component_name] = {"status": "failed", "step": "deploy_primary"}
                continue
            
            # Deploy to secondary region
            secondary_url = self.deploy_to_cloud_run(component_name, self.region_secondary)
            
            deployment_results[component_name] = {
                "status": "success",
                "primary_url": primary_url,
                "secondary_url": secondary_url
            }
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("📊 DEPLOYMENT SUMMARY")
        logger.info("=" * 60)
        
        for component, result in deployment_results.items():
            if result["status"] == "success":
                logger.info(f"✅ {component}: Successfully deployed")
                if isinstance(result.get("primary_url"), str):
                    logger.info(f"   Primary: {result['primary_url']}")
                if isinstance(result.get("secondary_url"), str):
                    logger.info(f"   Secondary: {result['secondary_url']}")
            else:
                logger.error(f"❌ {component}: Failed at {result.get('step', 'unknown')}")
        
        # Save deployment report
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_id": self.project_id,
            "deployment_results": deployment_results
        }
        
        report_file = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n📄 Deployment report saved: {report_file}")
        
        return all(r["status"] == "success" for r in deployment_results.values())
    
    def verify_deployment(self):
        """Verify deployed services are healthy"""
        logger.info("\n🔍 Verifying deployment health...")
        
        services = [
            ("content-pipeline", self.region_primary),
            ("content-pipeline", self.region_secondary),
            ("platform-agents", self.region_primary),
            ("platform-agents", self.region_secondary)
        ]
        
        for service_name, region in services:
            try:
                # Get service URL
                cmd = [
                    "gcloud", "run", "services", "describe", service_name,
                    "--region", region,
                    "--format", "value(status.url)"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    service_url = result.stdout.strip()
                    # Check health endpoint
                    import requests
                    response = requests.get(f"{service_url}/health", timeout=10)
                    if response.status_code == 200:
                        logger.info(f"✅ {service_name} ({region}): Healthy")
                    else:
                        logger.warning(f"⚠️ {service_name} ({region}): Unhealthy (status: {response.status_code})")
                else:
                    logger.warning(f"⚠️ {service_name} ({region}): Not found")
                    
            except Exception as e:
                logger.error(f"❌ Failed to verify {service_name} ({region}): {e}")

def main():
    """Main deployment function"""
    deployment = CloudDeployment()
    
    # Check if running Cloud Build or manual deployment
    if "--cloud-build" in sys.argv:
        logger.info("🏗️ Using Cloud Build for deployment")
        success = deployment.run_cloud_build()
    else:
        logger.info("🚀 Running manual deployment")
        success = deployment.deploy_all_components()
    
    if success:
        # Run migration script
        logger.info("\n📦 Running data migration...")
        try:
            subprocess.run([sys.executable, "migrate_to_cloud_storage.py"], check=True)
            logger.info("✅ Data migration completed")
        except Exception as e:
            logger.error(f"❌ Data migration failed: {e}")
        
        # Verify deployment
        deployment.verify_deployment()
        
        logger.info("\n✅ CLOUD DEPLOYMENT COMPLETE!")
        logger.info("\n📋 Next Steps:")
        logger.info("1. Configure global load balancer for multi-region")
        logger.info("2. Set up monitoring dashboards in Cloud Console")
        logger.info("3. Configure alerting policies")
        logger.info("4. Test end-to-end content generation")
    else:
        logger.error("\n❌ Deployment failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()