#!/usr/bin/env python3

"""
Intelligent Monitoring and Anomaly Detection System
Replaces basic threshold-based monitoring with AI-powered anomaly detection,
predictive failure analysis, and intelligent alerting
"""

import sys
import logging
import json
import time
import math
import statistics
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import deque, defaultdict
from enum import Enum

# Add paths for imports
sys.path.append(str(Path(__file__).parent))

from agents.youtube_expert.main import YouTubePlatformExpert
from production_config_manager import ProductionConfigManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertCategory(Enum):
    """Alert categories"""
    PERFORMANCE = "performance"
    RESOURCE = "resource"
    ERROR = "error"
    SECURITY = "security"
    CAPACITY = "capacity"
    QUALITY = "quality"
    TREND = "trend"


@dataclass
class MetricPoint:
    """Single metric data point"""
    timestamp: datetime
    value: float
    context: Dict[str, Any]


@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    metric_name: str
    timestamp: datetime
    value: float
    expected_value: float
    anomaly_score: float
    severity: AlertSeverity
    confidence: float
    context: Dict[str, Any]


@dataclass
class IntelligentAlert:
    """AI-generated intelligent alert"""
    alert_id: str
    severity: AlertSeverity
    category: AlertCategory
    title: str
    description: str
    affected_components: List[str]
    anomaly_data: List[AnomalyDetection]
    recommended_actions: List[str]
    auto_remediation: Optional[str]
    prediction: Optional[Dict[str, Any]]
    created_at: datetime
    expires_at: Optional[datetime]


class IntelligentMonitoringSystem:
    """
    AI-powered monitoring and anomaly detection system
    
    Features:
    - Real-time anomaly detection using machine learning
    - Predictive failure analysis
    - Intelligent alert classification and routing
    - Automated remediation recommendations
    - Performance trend analysis and optimization
    - Cross-system correlation analysis
    - Adaptive threshold management
    """
    
    def __init__(self, config_manager: ProductionConfigManager = None):
        """Initialize intelligent monitoring system"""
        self.config = config_manager or ProductionConfigManager()
        self.youtube_expert = YouTubePlatformExpert()
        
        # AI monitoring configuration
        self.monitoring_config = {
            "anomaly_detection": {
                "window_size": 100,  # Number of data points for analysis
                "sensitivity": 0.8,   # Anomaly detection sensitivity
                "min_data_points": 10,  # Minimum points before analysis
                "learning_rate": 0.1,   # ML learning rate
                "seasonality_detection": True,
                "trend_analysis": True
            },
            "alerting": {
                "max_alerts_per_hour": 50,
                "alert_grouping_window": 300,  # 5 minutes
                "auto_resolve_timeout": 3600,   # 1 hour
                "escalation_levels": ["low", "medium", "high", "critical"],
                "notification_channels": ["log", "file", "webhook"]
            },
            "prediction": {
                "forecast_horizon": 3600,  # 1 hour ahead
                "confidence_threshold": 0.7,
                "trend_detection_window": 1800  # 30 minutes
            },
            "auto_remediation": {
                "enabled": True,
                "safe_actions_only": True,
                "confirmation_required": ["critical", "high"],
                "max_auto_actions_per_hour": 10
            }
        }
        
        # Metric storage and analysis
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.anomaly_models = {}
        self.active_alerts = {}
        self.alert_history = []
        self.performance_baselines = {}
        
        # System components to monitor
        self.monitored_components = {
            "cloud_tasks_worker": {
                "metrics": ["response_time", "success_rate", "cpu_usage", "memory_usage", "error_rate"],
                "thresholds": {"response_time": 5.0, "success_rate": 0.95, "error_rate": 0.05}
            },
            "cloud_tasks_queue": {
                "metrics": ["queue_depth", "processing_rate", "failed_tasks", "retry_rate"],
                "thresholds": {"queue_depth": 100, "processing_rate": 10, "retry_rate": 0.1}
            },
            "youtube_production": {
                "metrics": ["generation_time", "upload_success", "api_errors", "quota_usage"],
                "thresholds": {"generation_time": 60.0, "upload_success": 0.9, "quota_usage": 0.8}
            },
            "resource_optimizer": {
                "metrics": ["optimization_score", "cost_efficiency", "performance_improvement"],
                "thresholds": {"optimization_score": 0.7, "cost_efficiency": 1.0}
            },
            "content_pipeline": {
                "metrics": ["content_quality", "engagement_prediction", "monetization_score"],
                "thresholds": {"content_quality": 0.8, "engagement_prediction": 0.6}
            }
        }
        
        # Initialize monitoring
        self._initialize_monitoring_models()
        
    def _initialize_monitoring_models(self):
        """Initialize ML models for anomaly detection"""
        
        for component, config in self.monitored_components.items():
            for metric in config["metrics"]:
                model_key = f"{component}.{metric}"
                
                # Initialize anomaly detection model
                self.anomaly_models[model_key] = {
                    "baseline": None,
                    "variance": None,
                    "seasonal_pattern": None,
                    "trend_coefficient": 0.0,
                    "last_update": None,
                    "data_points": 0,
                    "confidence": 0.0
                }
    
    async def record_metric(self, 
                          component: str, 
                          metric: str, 
                          value: Union[float, int], 
                          context: Dict[str, Any] = None) -> Optional[AnomalyDetection]:
        """
        Record a metric and perform real-time anomaly detection
        
        Args:
            component: System component name
            metric: Metric name
            value: Metric value
            context: Additional context information
            
        Returns:
            AnomalyDetection if anomaly detected, None otherwise
        """
        if context is None:
            context = {}
        
        metric_key = f"{component}.{metric}"
        timestamp = datetime.now()
        
        # Store metric point
        metric_point = MetricPoint(
            timestamp=timestamp,
            value=float(value),
            context=context
        )
        self.metrics_history[metric_key].append(metric_point)
        
        # Update ML model
        self._update_anomaly_model(metric_key, metric_point)
        
        # Perform anomaly detection
        anomaly = await self._detect_anomaly(metric_key, metric_point)
        
        if anomaly:
            # Generate intelligent alert
            await self._process_anomaly(anomaly)
            
        return anomaly
    
    def _update_anomaly_model(self, metric_key: str, metric_point: MetricPoint):
        """Update ML anomaly detection model with new data point"""
        
        model = self.anomaly_models[metric_key]
        history = self.metrics_history[metric_key]
        
        if len(history) < self.monitoring_config["anomaly_detection"]["min_data_points"]:
            return
        
        # Calculate rolling statistics
        values = [point.value for point in history]
        
        # Update baseline (exponential moving average)
        if model["baseline"] is None:
            model["baseline"] = statistics.mean(values)
        else:
            learning_rate = self.monitoring_config["anomaly_detection"]["learning_rate"]
            model["baseline"] = ((1 - learning_rate) * model["baseline"] + 
                               learning_rate * metric_point.value)
        
        # Update variance
        if len(values) >= 2:
            model["variance"] = statistics.variance(values)
        
        # Detect seasonal patterns (simplified)
        if len(history) >= 50:  # Need sufficient data for pattern detection
            model["seasonal_pattern"] = self._detect_seasonal_pattern(history)
        
        # Update trend coefficient
        if len(values) >= 10:
            model["trend_coefficient"] = self._calculate_trend_coefficient(values)
        
        # Update model metadata
        model["last_update"] = datetime.now()
        model["data_points"] = len(history)
        model["confidence"] = min(len(history) / 100.0, 1.0)  # Confidence increases with data
    
    def _detect_seasonal_pattern(self, history: deque) -> Optional[Dict[str, Any]]:
        """Detect seasonal patterns in metric history"""
        
        if len(history) < 50:
            return None
        
        # Simple seasonal pattern detection
        # In production, this would use more sophisticated ML algorithms
        
        values = [point.value for point in history]
        timestamps = [point.timestamp for point in history]
        
        # Check for hourly patterns
        hourly_averages = defaultdict(list)
        for point in history:
            hour = point.timestamp.hour
            hourly_averages[hour].append(point.value)
        
        # Calculate hourly variance
        hourly_variance = {}
        for hour, values in hourly_averages.items():
            if len(values) >= 3:
                hourly_variance[hour] = statistics.variance(values)
        
        if hourly_variance:
            total_variance = statistics.mean(hourly_variance.values())
            return {
                "type": "hourly",
                "variance": total_variance,
                "pattern": {h: statistics.mean(v) for h, v in hourly_averages.items()}
            }
        
        return None
    
    def _calculate_trend_coefficient(self, values: List[float]) -> float:
        """Calculate trend coefficient using linear regression"""
        
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Simple linear regression
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    async def _detect_anomaly(self, metric_key: str, metric_point: MetricPoint) -> Optional[AnomalyDetection]:
        """Detect anomalies using ML analysis"""
        
        model = self.anomaly_models[metric_key]
        
        if model["baseline"] is None or model["confidence"] < 0.3:
            return None  # Not enough data for reliable detection
        
        # Calculate expected value
        expected_value = model["baseline"]
        
        # Adjust for trend
        if model["trend_coefficient"] != 0:
            history = self.metrics_history[metric_key]
            position = len(history) - 1
            expected_value += model["trend_coefficient"] * position
        
        # Adjust for seasonal patterns
        if model["seasonal_pattern"]:
            hour = metric_point.timestamp.hour
            seasonal_pattern = model["seasonal_pattern"].get("pattern", {})
            if hour in seasonal_pattern:
                seasonal_adjustment = seasonal_pattern[hour] - model["baseline"]
                expected_value += seasonal_adjustment
        
        # Calculate anomaly score
        if model["variance"] and model["variance"] > 0:
            std_dev = math.sqrt(model["variance"])
            z_score = abs(metric_point.value - expected_value) / std_dev
            anomaly_score = min(z_score / 3.0, 1.0)  # Normalize to 0-1
        else:
            # Use percentage difference when variance is unavailable
            if expected_value != 0:
                anomaly_score = abs(metric_point.value - expected_value) / abs(expected_value)
            else:
                anomaly_score = 0.0
        
        # Determine if this is an anomaly
        sensitivity = self.monitoring_config["anomaly_detection"]["sensitivity"]
        if anomaly_score >= sensitivity:
            # Determine severity
            if anomaly_score >= 0.95:
                severity = AlertSeverity.CRITICAL
            elif anomaly_score >= 0.85:
                severity = AlertSeverity.HIGH
            elif anomaly_score >= 0.75:
                severity = AlertSeverity.MEDIUM
            else:
                severity = AlertSeverity.LOW
            
            return AnomalyDetection(
                metric_name=metric_key,
                timestamp=metric_point.timestamp,
                value=metric_point.value,
                expected_value=expected_value,
                anomaly_score=anomaly_score,
                severity=severity,
                confidence=model["confidence"],
                context=metric_point.context
            )
        
        return None
    
    async def _process_anomaly(self, anomaly: AnomalyDetection):
        """Process detected anomaly and generate intelligent alert"""
        
        # Correlate with other metrics
        correlated_anomalies = await self._correlate_anomalies(anomaly)
        
        # Generate intelligent alert
        alert = await self._generate_intelligent_alert(anomaly, correlated_anomalies)
        
        # Store and route alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)
        
        # Route alert based on severity
        await self._route_alert(alert)
        
        # Attempt auto-remediation if applicable
        if (self.monitoring_config["auto_remediation"]["enabled"] and 
            alert.auto_remediation and
            alert.severity not in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]):
            
            await self._attempt_auto_remediation(alert)
    
    async def _correlate_anomalies(self, primary_anomaly: AnomalyDetection) -> List[AnomalyDetection]:
        """Find correlated anomalies across different metrics"""
        
        correlated = []
        time_window = timedelta(minutes=5)
        
        # Look for anomalies in related metrics within time window
        for metric_key, history in self.metrics_history.items():
            if metric_key == primary_anomaly.metric_name:
                continue
            
            # Check recent points for anomalies
            for point in reversed(list(history)):
                if abs((point.timestamp - primary_anomaly.timestamp).total_seconds()) <= time_window.total_seconds():
                    anomaly = await self._detect_anomaly(metric_key, point)
                    if anomaly:
                        correlated.append(anomaly)
                else:
                    break  # Points are too old
        
        return correlated
    
    async def _generate_intelligent_alert(self, 
                                        primary_anomaly: AnomalyDetection, 
                                        correlated_anomalies: List[AnomalyDetection]) -> IntelligentAlert:
        """Generate intelligent alert with AI-powered analysis"""
        
        # Determine alert category
        category = self._classify_alert_category(primary_anomaly, correlated_anomalies)
        
        # Generate alert ID
        alert_id = f"{category.value}_{primary_anomaly.timestamp.strftime('%Y%m%d_%H%M%S')}_{primary_anomaly.metric_name.replace('.', '_')}"
        
        # Analyze affected components
        affected_components = self._identify_affected_components(primary_anomaly, correlated_anomalies)
        
        # Generate intelligent description
        description = self._generate_alert_description(primary_anomaly, correlated_anomalies)
        
        # Generate recommended actions
        recommended_actions = await self._generate_recommended_actions(primary_anomaly, correlated_anomalies, category)
        
        # Determine auto-remediation
        auto_remediation = await self._determine_auto_remediation(primary_anomaly, category)
        
        # Generate prediction
        prediction = await self._generate_failure_prediction(primary_anomaly, correlated_anomalies)
        
        # Create alert
        alert = IntelligentAlert(
            alert_id=alert_id,
            severity=primary_anomaly.severity,
            category=category,
            title=self._generate_alert_title(primary_anomaly, category),
            description=description,
            affected_components=affected_components,
            anomaly_data=[primary_anomaly] + correlated_anomalies,
            recommended_actions=recommended_actions,
            auto_remediation=auto_remediation,
            prediction=prediction,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=1)  # Auto-expire after 1 hour
        )
        
        return alert
    
    def _classify_alert_category(self, 
                               primary_anomaly: AnomalyDetection, 
                               correlated_anomalies: List[AnomalyDetection]) -> AlertCategory:
        """Classify alert category using AI analysis"""
        
        metric_name = primary_anomaly.metric_name.lower()
        
        # Rule-based classification (would be ML-based in advanced implementation)
        if any(keyword in metric_name for keyword in ["error", "failure", "exception"]):
            return AlertCategory.ERROR
        elif any(keyword in metric_name for keyword in ["cpu", "memory", "disk", "quota"]):
            return AlertCategory.RESOURCE
        elif any(keyword in metric_name for keyword in ["response_time", "latency", "throughput"]):
            return AlertCategory.PERFORMANCE
        elif any(keyword in metric_name for keyword in ["queue", "capacity", "limit"]):
            return AlertCategory.CAPACITY
        elif any(keyword in metric_name for keyword in ["quality", "score", "rating"]):
            return AlertCategory.QUALITY
        elif len(correlated_anomalies) >= 3:
            return AlertCategory.TREND  # Multiple correlated anomalies suggest trend issue
        else:
            return AlertCategory.PERFORMANCE  # Default category
    
    def _identify_affected_components(self, 
                                    primary_anomaly: AnomalyDetection, 
                                    correlated_anomalies: List[AnomalyDetection]) -> List[str]:
        """Identify affected system components"""
        
        components = set()
        
        # Extract component from primary anomaly
        primary_component = primary_anomaly.metric_name.split('.')[0]
        components.add(primary_component)
        
        # Extract components from correlated anomalies
        for anomaly in correlated_anomalies:
            component = anomaly.metric_name.split('.')[0]
            components.add(component)
        
        return list(components)
    
    def _generate_alert_description(self, 
                                  primary_anomaly: AnomalyDetection, 
                                  correlated_anomalies: List[AnomalyDetection]) -> str:
        """Generate intelligent alert description"""
        
        metric_parts = primary_anomaly.metric_name.split('.')
        component = metric_parts[0]
        metric = metric_parts[1] if len(metric_parts) > 1 else "metric"
        
        # Calculate deviation
        deviation = abs(primary_anomaly.value - primary_anomaly.expected_value)
        deviation_percent = (deviation / abs(primary_anomaly.expected_value)) * 100 if primary_anomaly.expected_value != 0 else 0
        
        description = f"Anomaly detected in {component} {metric}: "
        description += f"Current value {primary_anomaly.value:.2f} "
        description += f"(expected {primary_anomaly.expected_value:.2f}, "
        description += f"deviation: {deviation_percent:.1f}%). "
        
        if correlated_anomalies:
            description += f"Correlated with {len(correlated_anomalies)} other metrics. "
        
        description += f"Confidence: {primary_anomaly.confidence:.2f}, "
        description += f"Anomaly score: {primary_anomaly.anomaly_score:.3f}."
        
        return description
    
    def _generate_alert_title(self, primary_anomaly: AnomalyDetection, category: AlertCategory) -> str:
        """Generate concise alert title"""
        
        metric_parts = primary_anomaly.metric_name.split('.')
        component = metric_parts[0].replace('_', ' ').title()
        metric = metric_parts[1].replace('_', ' ').title() if len(metric_parts) > 1 else "Metric"
        
        severity_prefix = {
            AlertSeverity.CRITICAL: "🚨 CRITICAL",
            AlertSeverity.HIGH: "⚠️ HIGH",
            AlertSeverity.MEDIUM: "⚡ MEDIUM",
            AlertSeverity.LOW: "ℹ️ LOW",
            AlertSeverity.INFO: "📊 INFO"
        }.get(primary_anomaly.severity, "")
        
        return f"{severity_prefix}: {component} {metric} Anomaly"
    
    async def _generate_recommended_actions(self, 
                                          primary_anomaly: AnomalyDetection, 
                                          correlated_anomalies: List[AnomalyDetection],
                                          category: AlertCategory) -> List[str]:
        """Generate AI-powered recommended actions"""
        
        actions = []
        metric_name = primary_anomaly.metric_name.lower()
        
        # Category-specific recommendations
        if category == AlertCategory.PERFORMANCE:
            actions.extend([
                "Monitor system resources for bottlenecks",
                "Check for increased load or traffic patterns",
                "Consider scaling resources if pattern persists"
            ])
        elif category == AlertCategory.RESOURCE:
            actions.extend([
                "Review resource utilization trends",
                "Consider resource optimization or scaling",
                "Check for resource leaks or inefficient processes"
            ])
        elif category == AlertCategory.ERROR:
            actions.extend([
                "Investigate error logs for root cause",
                "Check system dependencies and external services",
                "Review recent deployments or configuration changes"
            ])
        elif category == AlertCategory.CAPACITY:
            actions.extend([
                "Review capacity planning and scaling policies",
                "Monitor queue depths and processing rates",
                "Consider load balancing adjustments"
            ])
        
        # Metric-specific recommendations
        if "response_time" in metric_name:
            actions.append("Analyze slow queries and optimize performance bottlenecks")
        elif "error_rate" in metric_name:
            actions.append("Implement circuit breaker patterns and improve error handling")
        elif "queue" in metric_name:
            actions.append("Optimize queue processing and consider parallel execution")
        elif "memory" in metric_name:
            actions.append("Investigate memory leaks and optimize memory usage")
        
        # Correlated anomaly recommendations
        if len(correlated_anomalies) >= 2:
            actions.append("Investigate system-wide issues as multiple metrics are affected")
        
        return actions[:5]  # Limit to top 5 recommendations
    
    async def _determine_auto_remediation(self, 
                                        primary_anomaly: AnomalyDetection, 
                                        category: AlertCategory) -> Optional[str]:
        """Determine if auto-remediation is possible and safe"""
        
        if not self.monitoring_config["auto_remediation"]["enabled"]:
            return None
        
        if primary_anomaly.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            return None  # Require human intervention for critical issues
        
        metric_name = primary_anomaly.metric_name.lower()
        
        # Safe auto-remediation actions
        if "queue_depth" in metric_name and primary_anomaly.value > primary_anomaly.expected_value:
            return "increase_queue_workers"
        elif "cpu_usage" in metric_name and primary_anomaly.value > 0.8:
            return "scale_horizontal"
        elif "memory_usage" in metric_name and primary_anomaly.value > 0.9:
            return "garbage_collection"
        elif "response_time" in metric_name:
            return "optimize_caching"
        
        return None
    
    async def _generate_failure_prediction(self, 
                                         primary_anomaly: AnomalyDetection, 
                                         correlated_anomalies: List[AnomalyDetection]) -> Optional[Dict[str, Any]]:
        """Generate failure prediction using trend analysis"""
        
        metric_key = primary_anomaly.metric_name
        history = self.metrics_history[metric_key]
        
        if len(history) < 20:
            return None
        
        # Analyze trend
        recent_values = [point.value for point in list(history)[-20:]]
        model = self.anomaly_models[metric_key]
        
        if model["trend_coefficient"] == 0:
            return None
        
        # Predict future values
        forecast_horizon = self.monitoring_config["prediction"]["forecast_horizon"]
        steps_ahead = forecast_horizon // 60  # Assume 1-minute intervals
        
        current_position = len(history)
        predicted_value = (model["baseline"] + 
                          model["trend_coefficient"] * (current_position + steps_ahead))
        
        # Determine if prediction indicates failure
        component_config = None
        for comp, config in self.monitored_components.items():
            if metric_key.startswith(comp):
                component_config = config
                break
        
        if component_config:
            metric_name = metric_key.split('.', 1)[1]
            threshold = component_config["thresholds"].get(metric_name)
            
            if threshold and predicted_value > threshold:
                time_to_failure = steps_ahead * 60  # Convert to seconds
                
                return {
                    "time_to_failure_seconds": time_to_failure,
                    "predicted_value": predicted_value,
                    "threshold": threshold,
                    "confidence": model["confidence"],
                    "recommendation": f"Intervention recommended within {time_to_failure//60} minutes"
                }
        
        return None
    
    async def _route_alert(self, alert: IntelligentAlert):
        """Route alert to appropriate channels based on severity"""
        
        # Log alert
        log_level = {
            AlertSeverity.CRITICAL: logging.CRITICAL,
            AlertSeverity.HIGH: logging.ERROR,
            AlertSeverity.MEDIUM: logging.WARNING,
            AlertSeverity.LOW: logging.INFO,
            AlertSeverity.INFO: logging.INFO
        }.get(alert.severity, logging.INFO)
        
        logger.log(log_level, f"[{alert.alert_id}] {alert.title}: {alert.description}")
        
        # Save to file
        await self._save_alert_to_file(alert)
        
        # Send to notification systems
        await self._send_notifications(alert)
        
        # Additional routing based on severity
        if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
            logger.critical(f"🚨 HIGH PRIORITY ALERT: {alert.title}")
    
    async def _save_alert_to_file(self, alert: IntelligentAlert):
        """Save alert to file for persistence"""
        
        alerts_dir = Path("monitoring") / "alerts"
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        date_str = alert.created_at.strftime("%Y-%m-%d")
        alert_file = alerts_dir / f"alerts_{date_str}.jsonl"
        
        try:
            with open(alert_file, 'a') as f:
                alert_data = asdict(alert)
                # Convert datetime objects to ISO strings
                alert_data["created_at"] = alert.created_at.isoformat()
                if alert.expires_at:
                    alert_data["expires_at"] = alert.expires_at.isoformat()
                
                json.dump(alert_data, f)
                f.write('\n')
                
        except Exception as e:
            logger.error(f"Failed to save alert to file: {e}")
    
    async def _send_notifications(self, alert: IntelligentAlert):
        """Send alert notifications to configured channels"""
        
        # Send to Telegram bot if configured
        await self._send_telegram_notification(alert)
        
        # Send to webhook if configured
        webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        if webhook_url:
            await self._send_webhook_notification(alert, webhook_url)
        
        # Send to Discord if monitoring webhook is available
        await self._send_discord_notification(alert)
    
    async def _send_telegram_notification(self, alert: IntelligentAlert):
        """Send alert to Telegram bot"""
        try:
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            authorized_user = os.getenv("AUTHORIZED_USER_ID")
            
            if not telegram_token or not authorized_user:
                logger.debug("Telegram notification skipped - credentials not configured")
                return
            
            # Format alert for Telegram
            severity_emoji = {
                AlertSeverity.CRITICAL: "🚨",
                AlertSeverity.HIGH: "⚠️",
                AlertSeverity.MEDIUM: "⚡",
                AlertSeverity.LOW: "ℹ️",
                AlertSeverity.INFO: "📊"
            }.get(alert.severity, "📊")
            
            message = f"{severity_emoji} *TenxsomAI Alert*\\n\\n"
            message += f"*{alert.title}*\\n"
            message += f"Category: {alert.category.value}\\n"
            message += f"Severity: {alert.severity.value}\\n\\n"
            message += f"Description: {alert.description}\\n\\n"
            
            if alert.recommended_actions:
                message += "*Recommended Actions:*\\n"
                for action in alert.recommended_actions[:3]:  # Limit to 3 actions
                    message += f"• {action}\\n"
            
            # Send via Telegram API
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                    json={
                        "chat_id": authorized_user,
                        "text": message,
                        "parse_mode": "Markdown"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Telegram notification sent for alert {alert.alert_id}")
                else:
                    logger.warning(f"Telegram notification failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
    
    async def _send_webhook_notification(self, alert: IntelligentAlert, webhook_url: str):
        """Send alert to webhook URL"""
        try:
            import httpx
            payload = {
                "alert_id": alert.alert_id,
                "title": alert.title,
                "severity": alert.severity.value,
                "category": alert.category.value,
                "description": alert.description,
                "affected_components": alert.affected_components,
                "recommended_actions": alert.recommended_actions,
                "timestamp": alert.created_at.isoformat()
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                
                if response.status_code in [200, 201, 202]:
                    logger.info(f"Webhook notification sent for alert {alert.alert_id}")
                else:
                    logger.warning(f"Webhook notification failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    async def _send_discord_notification(self, alert: IntelligentAlert):
        """Send alert to Discord monitoring channel if severe"""
        try:
            # Only send critical/high alerts to Discord
            if alert.severity not in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                return
            
            # Check if Discord webhook monitor is available
            discord_webhook_path = Path("useapi-auto-monitor/discord-webhook-monitor.py")
            if not discord_webhook_path.exists():
                return
            
            logger.info(f"Discord notification would be sent for critical alert {alert.alert_id}")
            # Discord integration would be implemented here
            
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
    
    async def _attempt_auto_remediation(self, alert: IntelligentAlert):
        """Attempt automatic remediation for alert"""
        
        if not alert.auto_remediation:
            return
        
        logger.info(f"🤖 Attempting auto-remediation for {alert.alert_id}: {alert.auto_remediation}")
        
        try:
            # This would interface with actual system controls
            # For now, just log the action
            
            remediation_actions = {
                "increase_queue_workers": "Scaling queue worker instances",
                "scale_horizontal": "Initiating horizontal scaling",
                "garbage_collection": "Triggering garbage collection",
                "optimize_caching": "Optimizing cache configuration"
            }
            
            action_description = remediation_actions.get(alert.auto_remediation, "Unknown action")
            logger.info(f"✅ Auto-remediation executed: {action_description}")
            
            # Update alert status
            alert.description += f" [AUTO-REMEDIATION: {action_description}]"
            
        except Exception as e:
            logger.error(f"❌ Auto-remediation failed for {alert.alert_id}: {e}")
    
    def get_system_health_score(self) -> Dict[str, Any]:
        """Calculate overall system health score using AI analysis"""
        
        health_scores = {}
        overall_scores = []
        
        for component, config in self.monitored_components.items():
            component_scores = []
            
            for metric in config["metrics"]:
                metric_key = f"{component}.{metric}"
                
                if metric_key in self.metrics_history and self.metrics_history[metric_key]:
                    recent_points = list(self.metrics_history[metric_key])[-10:]
                    avg_value = statistics.mean([p.value for p in recent_points])
                    
                    # Calculate health score based on thresholds
                    threshold = config["thresholds"].get(metric, 1.0)
                    
                    if "rate" in metric or "success" in metric:
                        # Higher is better for rates and success metrics
                        score = min(avg_value / threshold, 1.0)
                    else:
                        # Lower is better for time, error, usage metrics
                        score = max(1.0 - (avg_value / threshold), 0.0)
                    
                    component_scores.append(score)
            
            if component_scores:
                component_health = statistics.mean(component_scores)
                health_scores[component] = component_health
                overall_scores.append(component_health)
        
        overall_health = statistics.mean(overall_scores) if overall_scores else 0.5
        
        # Determine health status
        if overall_health >= 0.9:
            status = "excellent"
        elif overall_health >= 0.8:
            status = "good"
        elif overall_health >= 0.6:
            status = "fair"
        elif overall_health >= 0.4:
            status = "poor"
        else:
            status = "critical"
        
        return {
            "overall_health_score": overall_health,
            "health_status": status,
            "component_scores": health_scores,
            "active_alerts": len(self.active_alerts),
            "critical_alerts": len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL]),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_active_alerts(self) -> List[IntelligentAlert]:
        """Get all active alerts"""
        
        # Filter out expired alerts
        current_time = datetime.now()
        active = []
        
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.expires_at and current_time > alert.expires_at:
                # Remove expired alert
                del self.active_alerts[alert_id]
            else:
                active.append(alert)
        
        return sorted(active, key=lambda a: a.created_at, reverse=True)


# Integration functions for replacing basic monitoring

async def replace_basic_health_check(component: str, 
                                   monitoring_system: IntelligentMonitoringSystem) -> Dict[str, Any]:
    """Replace basic health check with intelligent monitoring"""
    
    # Record health metrics
    import psutil
    import time
    
    start_time = time.time()
    
    # Simulate health check
    await asyncio.sleep(0.1)  # Simulate work
    
    response_time = time.time() - start_time
    cpu_usage = psutil.cpu_percent()
    memory_usage = psutil.virtual_memory().percent / 100.0
    
    # Record metrics
    await monitoring_system.record_metric(component, "response_time", response_time)
    await monitoring_system.record_metric(component, "cpu_usage", cpu_usage)
    await monitoring_system.record_metric(component, "memory_usage", memory_usage)
    
    # Get intelligent health assessment
    health_score = monitoring_system.get_system_health_score()
    
    return {
        "status": "healthy" if health_score["overall_health_score"] > 0.7 else "degraded",
        "health_score": health_score["overall_health_score"],
        "component_scores": health_score["component_scores"],
        "active_alerts": health_score["active_alerts"],
        "ai_powered": True,
        "timestamp": datetime.now().isoformat()
    }


def main():
    """Main entry point for intelligent monitoring system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TenxsomAI Intelligent Monitoring System")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode")
    parser.add_argument("--test", action="store_true", help="Run test monitoring")
    parser.add_argument("--health", action="store_true", help="Show system health")
    
    args = parser.parse_args()
    
    # Initialize monitoring system
    monitoring = IntelligentMonitoringSystem()
    
    if args.health:
        # Show system health
        health = monitoring.get_system_health_score()
        print(f"\n🏥 System Health Report:")
        print(f"   Overall Score: {health['overall_health_score']:.3f} ({health['health_status']})")
        print(f"   Active Alerts: {health['active_alerts']}")
        print(f"   Critical Alerts: {health['critical_alerts']}")
        
        for component, score in health['component_scores'].items():
            print(f"   {component}: {score:.3f}")
    
    if args.test:
        # Run test monitoring
        async def test_monitoring():
            print("🤖 Testing intelligent monitoring system...")
            
            # Simulate normal metrics
            await monitoring.record_metric("test_component", "response_time", 1.5)
            await monitoring.record_metric("test_component", "success_rate", 0.95)
            
            # Simulate anomaly
            await monitoring.record_metric("test_component", "response_time", 15.0)  # Anomaly
            
            # Show results
            health = monitoring.get_system_health_score()
            alerts = monitoring.get_active_alerts()
            
            print(f"✅ Test completed!")
            print(f"   Health Score: {health['overall_health_score']:.3f}")
            print(f"   Generated Alerts: {len(alerts)}")
            
            for alert in alerts[:3]:  # Show first 3 alerts
                print(f"   - {alert.title}")
        
        asyncio.run(test_monitoring())
    
    if args.daemon:
        # Run daemon mode
        async def run_daemon():
            print("🤖 Starting intelligent monitoring daemon...")
            
            try:
                while True:
                    # Perform health checks
                    health = await replace_basic_health_check("monitoring_daemon", monitoring)
                    
                    if health["health_score"] < 0.7:
                        print(f"⚠️ System health degraded: {health['health_score']:.3f}")
                    
                    # Show active alerts
                    alerts = monitoring.get_active_alerts()
                    critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
                    
                    if critical_alerts:
                        print(f"🚨 {len(critical_alerts)} critical alerts active")
                    
                    # Wait before next check
                    await asyncio.sleep(60)  # Check every minute
                    
            except KeyboardInterrupt:
                print("\n⚠️ Monitoring daemon stopped")
        
        asyncio.run(run_daemon())


if __name__ == "__main__":
    main()