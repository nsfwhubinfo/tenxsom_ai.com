#!/usr/bin/env python3
"""
Migrate local analytics and monitoring data to Google Cloud Storage
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from google.cloud import storage
from google.cloud import monitoring_v3
from google.cloud import logging as cloud_logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudMigration:
    """Handle migration of local data to cloud services"""
    
    def __init__(self, project_id="tenxsom-ai-1631088"):
        self.project_id = project_id
        self.storage_client = storage.Client(project=project_id)
        self.monitoring_client = monitoring_v3.MetricServiceClient()
        self.logging_client = cloud_logging.Client(project=project_id)
        
        # Configure buckets
        self.analytics_bucket = "tenxsom-analytics"
        self.monitoring_bucket = "tenxsom-monitoring"
        self.logs_bucket = "tenxsom-logs"
        
    def create_buckets(self):
        """Create Cloud Storage buckets if they don't exist"""
        buckets = [
            (self.analytics_bucket, "Analytics data storage"),
            (self.monitoring_bucket, "Monitoring metrics storage"),
            (self.logs_bucket, "Application logs storage")
        ]
        
        for bucket_name, description in buckets:
            try:
                bucket = self.storage_client.create_bucket(
                    bucket_name,
                    location="us-central1"
                )
                logger.info(f"✅ Created bucket: {bucket_name} - {description}")
                
                # Set lifecycle rules for cost optimization
                bucket.add_lifecycle_rule(
                    action={"type": "SetStorageClass", "storageClass": "NEARLINE"},
                    condition={"age": 30}  # Move to nearline after 30 days
                )
                bucket.add_lifecycle_rule(
                    action={"type": "SetStorageClass", "storageClass": "COLDLINE"},
                    condition={"age": 90}  # Move to coldline after 90 days
                )
                bucket.patch()
                
            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"✓ Bucket already exists: {bucket_name}")
                else:
                    logger.error(f"❌ Failed to create bucket {bucket_name}: {e}")
    
    def migrate_analytics_data(self):
        """Migrate local analytics data to Cloud Storage"""
        logger.info("📊 Migrating analytics data to Cloud Storage...")
        
        analytics_path = Path("analytics")
        if not analytics_path.exists():
            logger.warning("No analytics directory found")
            return
        
        bucket = self.storage_client.bucket(self.analytics_bucket)
        migrated_count = 0
        
        # Migrate all JSON files
        for json_file in analytics_path.glob("**/*.json"):
            try:
                # Create cloud path preserving directory structure
                relative_path = json_file.relative_to(analytics_path)
                blob_name = f"historical/{relative_path}"
                
                blob = bucket.blob(blob_name)
                blob.upload_from_filename(str(json_file))
                
                # Set metadata
                blob.metadata = {
                    "migrated_at": datetime.utcnow().isoformat(),
                    "original_path": str(json_file)
                }
                blob.patch()
                
                migrated_count += 1
                logger.info(f"  ✓ Migrated: {relative_path}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to migrate {json_file}: {e}")
        
        logger.info(f"✅ Migrated {migrated_count} analytics files")
    
    def migrate_monitoring_data(self):
        """Migrate monitoring data to Cloud Monitoring"""
        logger.info("📈 Migrating monitoring data to Cloud Monitoring...")
        
        monitoring_path = Path("monitoring")
        if not monitoring_path.exists():
            logger.warning("No monitoring directory found")
            return
        
        # Migrate dashboard configurations
        dashboard_file = monitoring_path / "dashboard.json"
        if dashboard_file.exists():
            bucket = self.storage_client.bucket(self.monitoring_bucket)
            blob = bucket.blob("dashboards/production_dashboard.json")
            blob.upload_from_filename(str(dashboard_file))
            logger.info("  ✓ Migrated dashboard configuration")
        
        # Setup Cloud Monitoring metrics
        self._setup_cloud_monitoring_metrics()
    
    def _setup_cloud_monitoring_metrics(self):
        """Set up custom metrics in Cloud Monitoring"""
        project_name = f"projects/{self.project_id}"
        
        custom_metrics = [
            {
                "type": "custom.googleapis.com/tenxsom/videos_generated",
                "display_name": "Videos Generated",
                "description": "Number of videos generated per day",
                "metric_kind": monitoring_v3.MetricDescriptor.MetricKind.GAUGE,
                "value_type": monitoring_v3.MetricDescriptor.ValueType.INT64
            },
            {
                "type": "custom.googleapis.com/tenxsom/processing_time",
                "display_name": "Video Processing Time",
                "description": "Time taken to process videos in seconds",
                "metric_kind": monitoring_v3.MetricDescriptor.MetricKind.GAUGE,
                "value_type": monitoring_v3.MetricDescriptor.ValueType.DOUBLE
            },
            {
                "type": "custom.googleapis.com/tenxsom/upload_success_rate",
                "display_name": "Upload Success Rate",
                "description": "Percentage of successful uploads",
                "metric_kind": monitoring_v3.MetricDescriptor.MetricKind.GAUGE,
                "value_type": monitoring_v3.MetricDescriptor.ValueType.DOUBLE
            },
            {
                "type": "custom.googleapis.com/tenxsom/daily_cost",
                "display_name": "Daily Cost",
                "description": "Daily cost of video generation",
                "metric_kind": monitoring_v3.MetricDescriptor.MetricKind.GAUGE,
                "value_type": monitoring_v3.MetricDescriptor.ValueType.DOUBLE
            }
        ]
        
        for metric_config in custom_metrics:
            try:
                descriptor = monitoring_v3.MetricDescriptor()
                descriptor.type = metric_config["type"]
                descriptor.display_name = metric_config["display_name"]
                descriptor.description = metric_config["description"]
                descriptor.metric_kind = metric_config["metric_kind"]
                descriptor.value_type = metric_config["value_type"]
                
                # Add label descriptors
                label = descriptor.labels.add()
                label.key = "environment"
                label.value_type = monitoring_v3.LabelDescriptor.ValueType.STRING
                label.description = "Deployment environment"
                
                self.monitoring_client.create_metric_descriptor(
                    name=project_name,
                    metric_descriptor=descriptor
                )
                
                logger.info(f"  ✓ Created metric: {metric_config['display_name']}")
                
            except Exception as e:
                if "already exists" in str(e):
                    logger.info(f"  ✓ Metric already exists: {metric_config['display_name']}")
                else:
                    logger.error(f"  ❌ Failed to create metric: {e}")
    
    def migrate_logs(self):
        """Migrate local logs to Cloud Logging"""
        logger.info("📝 Migrating logs to Cloud Logging...")
        
        # Setup structured logging
        handler = self.logging_client.get_default_handler()
        cloud_logger = logging.getLogger("tenxsom-ai")
        cloud_logger.setLevel(logging.INFO)
        cloud_logger.addHandler(handler)
        
        # Migrate existing log files
        logs_path = Path("logs")
        if logs_path.exists():
            bucket = self.storage_client.bucket(self.logs_bucket)
            
            for log_file in logs_path.glob("**/*.log"):
                try:
                    # Archive to Cloud Storage
                    relative_path = log_file.relative_to(logs_path)
                    blob_name = f"archive/{relative_path}"
                    blob = bucket.blob(blob_name)
                    blob.upload_from_filename(str(log_file))
                    
                    logger.info(f"  ✓ Archived log: {relative_path}")
                    
                except Exception as e:
                    logger.error(f"  ❌ Failed to archive {log_file}: {e}")
        
        logger.info("✅ Log migration complete")
    
    def setup_cloud_native_analytics(self):
        """Set up cloud-native analytics integration"""
        logger.info("🔧 Setting up cloud-native analytics...")
        
        # Create analytics configuration
        analytics_config = {
            "version": "1.0",
            "storage": {
                "analytics_bucket": self.analytics_bucket,
                "monitoring_bucket": self.monitoring_bucket,
                "logs_bucket": self.logs_bucket
            },
            "metrics": {
                "enabled": True,
                "custom_metrics": [
                    "videos_generated",
                    "processing_time",
                    "upload_success_rate",
                    "daily_cost"
                ]
            },
            "logging": {
                "enabled": True,
                "structured_logging": True,
                "log_level": "INFO"
            },
            "alerts": {
                "enabled": True,
                "channels": ["email", "slack"],
                "policies": [
                    {
                        "name": "high_error_rate",
                        "threshold": 0.1,
                        "duration": "5m"
                    },
                    {
                        "name": "low_throughput",
                        "threshold": 50,
                        "duration": "1h"
                    }
                ]
            }
        }
        
        # Save configuration
        config_path = Path("cloud_analytics_config.json")
        with open(config_path, "w") as f:
            json.dump(analytics_config, f, indent=2)
        
        logger.info(f"✅ Created cloud analytics configuration: {config_path}")
        
        # Upload to Cloud Storage
        bucket = self.storage_client.bucket(self.analytics_bucket)
        blob = bucket.blob("config/analytics_config.json")
        blob.upload_from_filename(str(config_path))
        
        return analytics_config
    
    def create_monitoring_dashboard(self):
        """Create Cloud Monitoring dashboard"""
        logger.info("📊 Creating Cloud Monitoring dashboard...")
        
        # Dashboard configuration
        dashboard_config = {
            "displayName": "TenxsomAI Production Dashboard",
            "gridLayout": {
                "widgets": [
                    {
                        "title": "Videos Generated (Daily)",
                        "xyChart": {
                            "dataSets": [{
                                "timeSeriesQuery": {
                                    "timeSeriesFilter": {
                                        "filter": 'metric.type="custom.googleapis.com/tenxsom/videos_generated"'
                                    }
                                }
                            }]
                        }
                    },
                    {
                        "title": "Processing Time (Average)",
                        "xyChart": {
                            "dataSets": [{
                                "timeSeriesQuery": {
                                    "timeSeriesFilter": {
                                        "filter": 'metric.type="custom.googleapis.com/tenxsom/processing_time"'
                                    }
                                }
                            }]
                        }
                    },
                    {
                        "title": "Upload Success Rate",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": 'metric.type="custom.googleapis.com/tenxsom/upload_success_rate"'
                                }
                            }
                        }
                    },
                    {
                        "title": "Daily Cost",
                        "scorecard": {
                            "timeSeriesQuery": {
                                "timeSeriesFilter": {
                                    "filter": 'metric.type="custom.googleapis.com/tenxsom/daily_cost"'
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        # Save dashboard config
        dashboard_path = Path("monitoring_dashboard.json")
        with open(dashboard_path, "w") as f:
            json.dump(dashboard_config, f, indent=2)
        
        logger.info(f"✅ Created dashboard configuration: {dashboard_path}")
        
        # Note: Actual dashboard creation requires Dashboard API
        logger.info("📌 To create dashboard in Cloud Console:")
        logger.info("   1. Go to Cloud Monitoring > Dashboards")
        logger.info("   2. Click 'Create Dashboard'")
        logger.info("   3. Import the configuration from monitoring_dashboard.json")
    
    def run_full_migration(self):
        """Run complete migration to cloud services"""
        logger.info("🚀 Starting full cloud migration...")
        logger.info("=" * 60)
        
        # Create buckets
        self.create_buckets()
        
        # Migrate data
        self.migrate_analytics_data()
        self.migrate_monitoring_data()
        self.migrate_logs()
        
        # Setup cloud-native services
        analytics_config = self.setup_cloud_native_analytics()
        self.create_monitoring_dashboard()
        
        logger.info("=" * 60)
        logger.info("✅ CLOUD MIGRATION COMPLETE!")
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("1. Update application code to use Cloud Storage APIs")
        logger.info("2. Configure alert policies in Cloud Monitoring")
        logger.info("3. Set up log-based metrics for advanced analytics")
        logger.info("4. Test cloud-native monitoring and analytics")
        
        return {
            "status": "success",
            "analytics_config": analytics_config,
            "buckets_created": [
                self.analytics_bucket,
                self.monitoring_bucket,
                self.logs_bucket
            ]
        }

def main():
    """Main migration function"""
    try:
        migration = CloudMigration()
        result = migration.run_full_migration()
        
        # Save migration report
        report_path = f"cloud_migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, "w") as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"\n📄 Migration report saved: {report_path}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()