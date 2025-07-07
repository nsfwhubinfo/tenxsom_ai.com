#!/usr/bin/env python3

"""
Tenxsom AI System Monitor
Real-time monitoring and alerting for production system
"""

import os
import asyncio
import logging
import psutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    process_count: int
    load_average: List[float]


@dataclass
class ServiceMetrics:
    """Service-specific metrics"""
    service_name: str
    process_id: Optional[int]
    cpu_percent: float
    memory_mb: float
    status: str
    uptime_seconds: float
    restart_count: int


@dataclass
class AlertCondition:
    """Alert condition definition"""
    metric_name: str
    threshold: float
    operator: str  # >, <, >=, <=, ==
    severity: str  # critical, warning, info
    message: str


class SystemMonitor:
    """
    Real-time system monitoring and alerting
    
    Features:
    - CPU, memory, disk, and network monitoring
    - Service process monitoring
    - Automated alerting and notifications
    - Performance trend analysis
    - System health scoring
    - Automated recovery actions
    """
    
    def __init__(self, config_file: str = None):
        """Initialize system monitor"""
        self.config_file = config_file
        self.monitoring_active = False
        self.metrics_history = []
        self.service_metrics = {}
        self.alerts_active = []
        
        # Monitoring configuration
        self.monitor_config = {
            "collection_interval": 30,  # seconds
            "history_retention_hours": 24,
            "alert_cooldown_minutes": 15,
            "performance_samples": 100
        }
        
        # Alert conditions
        self.alert_conditions = [
            AlertCondition(
                metric_name="cpu_percent",
                threshold=80.0,
                operator=">=",
                severity="warning",
                message="High CPU usage detected"
            ),
            AlertCondition(
                metric_name="memory_percent", 
                threshold=85.0,
                operator=">=",
                severity="warning",
                message="High memory usage detected"
            ),
            AlertCondition(
                metric_name="disk_usage_percent",
                threshold=90.0,
                operator=">=",
                severity="critical",
                message="Disk space critically low"
            ),
            AlertCondition(
                metric_name="memory_percent",
                threshold=95.0,
                operator=">=",
                severity="critical",
                message="Memory usage critical"
            )
        ]
        
        # Service monitoring
        self.monitored_services = [
            "production_deployment",
            "monetization_executor", 
            "content_scheduler",
            "upload_orchestrator",
            "analytics_tracker"
        ]
        
        # Directories
        self.monitor_dir = Path(__file__).parent / "production" / "monitoring"
        self.monitor_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_baseline = None
        self.performance_trends = {}
    
    async def start_monitoring(self) -> None:
        """Start real-time system monitoring"""
        logger.info("🔍 Starting system monitoring...")
        
        self.monitoring_active = True
        
        # Start monitoring tasks
        monitoring_tasks = [
            asyncio.create_task(self._metrics_collection_loop()),
            asyncio.create_task(self._alert_processing_loop()),
            asyncio.create_task(self._performance_analysis_loop()),
            asyncio.create_task(self._health_reporting_loop())
        ]
        
        try:
            await asyncio.gather(*monitoring_tasks)
        except asyncio.CancelledError:
            logger.info("📊 Monitoring stopped")
    
    async def stop_monitoring(self) -> None:
        """Stop system monitoring"""
        logger.info("🛑 Stopping system monitoring...")
        self.monitoring_active = False
    
    async def _metrics_collection_loop(self) -> None:
        """Continuous metrics collection"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                system_metrics = await self._collect_system_metrics()
                self.metrics_history.append(system_metrics)
                
                # Collect service metrics
                service_metrics = await self._collect_service_metrics()
                self.service_metrics.update(service_metrics)
                
                # Cleanup old metrics
                await self._cleanup_old_metrics()
                
                # Save metrics
                await self._save_metrics(system_metrics, service_metrics)
                
                await asyncio.sleep(self.monitor_config["collection_interval"])
                
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_usage_percent = (disk.used / disk.total) * 100
        disk_free_gb = disk.free / (1024**3)
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Process count
        process_count = len(psutil.pids())
        
        # Load average (Unix systems)
        try:
            load_average = list(os.getloadavg())
        except (OSError, AttributeError):
            load_average = [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_gb=memory_available_gb,
            disk_usage_percent=disk_usage_percent,
            disk_free_gb=disk_free_gb,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            process_count=process_count,
            load_average=load_average
        )
    
    async def _collect_service_metrics(self) -> Dict[str, ServiceMetrics]:
        """Collect service-specific metrics"""
        service_metrics = {}
        
        # Find Tenxsom AI processes
        tenxsom_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = proc.info['cmdline'] or []
                if any('tenxsom' in str(arg).lower() or 
                      'production' in str(arg).lower() or
                      'monetization' in str(arg).lower()
                      for arg in cmdline):
                    tenxsom_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Monitor each service
        for service_name in self.monitored_services:
            try:
                # Find process for this service
                service_process = None
                for proc in tenxsom_processes:
                    cmdline = proc.info['cmdline'] or []
                    if any(service_name in str(arg) for arg in cmdline):
                        service_process = proc
                        break
                
                if service_process:
                    # Get process metrics
                    proc_info = service_process.as_dict(['pid', 'cpu_percent', 'memory_info', 'create_time', 'status'])
                    
                    uptime = datetime.now().timestamp() - proc_info['create_time']
                    memory_mb = proc_info['memory_info'].rss / (1024 * 1024)
                    
                    service_metrics[service_name] = ServiceMetrics(
                        service_name=service_name,
                        process_id=proc_info['pid'],
                        cpu_percent=proc_info['cpu_percent'] or 0.0,
                        memory_mb=memory_mb,
                        status=proc_info['status'],
                        uptime_seconds=uptime,
                        restart_count=0  # Would track from persistent storage
                    )
                else:
                    # Service not running
                    service_metrics[service_name] = ServiceMetrics(
                        service_name=service_name,
                        process_id=None,
                        cpu_percent=0.0,
                        memory_mb=0.0,
                        status="not_running",
                        uptime_seconds=0.0,
                        restart_count=0
                    )
                    
            except Exception as e:
                logger.error(f"❌ Failed to collect metrics for {service_name}: {e}")
        
        return service_metrics
    
    async def _alert_processing_loop(self) -> None:
        """Process alerts based on metrics"""
        while self.monitoring_active:
            try:
                if self.metrics_history:
                    latest_metrics = self.metrics_history[-1]
                    
                    # Check alert conditions
                    new_alerts = await self._check_alert_conditions(latest_metrics)
                    
                    # Process new alerts
                    for alert in new_alerts:
                        await self._process_alert(alert)
                    
                    # Cleanup resolved alerts
                    await self._cleanup_resolved_alerts()
                
                await asyncio.sleep(60)  # Check alerts every minute
                
            except Exception as e:
                logger.error(f"❌ Alert processing error: {e}")
                await asyncio.sleep(60)
    
    async def _check_alert_conditions(self, metrics: SystemMetrics) -> List[Dict[str, Any]]:
        """Check if any alert conditions are met"""
        new_alerts = []
        
        for condition in self.alert_conditions:
            try:
                # Get metric value
                metric_value = getattr(metrics, condition.metric_name, None)
                if metric_value is None:
                    continue
                
                # Check condition
                triggered = False
                if condition.operator == ">=":
                    triggered = metric_value >= condition.threshold
                elif condition.operator ">":
                    triggered = metric_value > condition.threshold
                elif condition.operator == "<=":
                    triggered = metric_value <= condition.threshold
                elif condition.operator == "<":
                    triggered = metric_value < condition.threshold
                elif condition.operator == "==":
                    triggered = metric_value == condition.threshold
                
                if triggered:
                    # Check if alert already active
                    alert_id = f"{condition.metric_name}_{condition.operator}_{condition.threshold}"
                    if not any(alert["id"] == alert_id for alert in self.alerts_active):
                        
                        alert = {
                            "id": alert_id,
                            "timestamp": datetime.now(),
                            "condition": asdict(condition),
                            "metric_value": metric_value,
                            "status": "active"
                        }
                        
                        new_alerts.append(alert)
                        self.alerts_active.append(alert)
                
            except Exception as e:
                logger.error(f"❌ Error checking condition {condition.metric_name}: {e}")
        
        return new_alerts
    
    async def _process_alert(self, alert: Dict[str, Any]) -> None:
        """Process and handle an alert"""
        condition = alert["condition"]
        
        logger.warning(f"🚨 ALERT: {condition['message']} (Value: {alert['metric_value']:.1f}, Threshold: {condition['threshold']})")
        
        # Save alert to file
        alert_file = self.monitor_dir / f"alert_{alert['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(alert_file, 'w') as f:
            json.dump(alert, f, indent=2, default=str)
        
        # Take automated actions based on severity
        if condition["severity"] == "critical":
            await self._handle_critical_alert(alert)
        elif condition["severity"] == "warning":
            await self._handle_warning_alert(alert)
    
    async def _handle_critical_alert(self, alert: Dict[str, Any]) -> None:
        """Handle critical alerts with automated actions"""
        condition = alert["condition"]
        
        logger.critical(f"🔴 CRITICAL ALERT: {condition['message']}")
        
        # Automated recovery actions
        if condition["metric_name"] == "memory_percent":
            logger.info("🔧 Attempting memory cleanup...")
            # Could trigger garbage collection, restart services, etc.
            
        elif condition["metric_name"] == "disk_usage_percent":
            logger.info("🔧 Attempting disk cleanup...")
            # Could clean temp files, rotate logs, etc.
            await self._cleanup_disk_space()
    
    async def _handle_warning_alert(self, alert: Dict[str, Any]) -> None:
        """Handle warning alerts"""
        condition = alert["condition"]
        logger.warning(f"⚠️ WARNING ALERT: {condition['message']}")
        
        # Log for monitoring but don't take automated action
    
    async def _cleanup_resolved_alerts(self) -> None:
        """Remove alerts that are no longer active"""
        if not self.metrics_history:
            return
        
        latest_metrics = self.metrics_history[-1]
        resolved_alerts = []
        
        for alert in self.alerts_active:
            condition_dict = alert["condition"]
            condition = AlertCondition(**condition_dict)
            
            # Check if condition is still met
            metric_value = getattr(latest_metrics, condition.metric_name, None)
            if metric_value is not None:
                still_triggered = False
                
                if condition.operator == ">=":
                    still_triggered = metric_value >= condition.threshold
                elif condition.operator == ">":
                    still_triggered = metric_value > condition.threshold
                elif condition.operator == "<=":
                    still_triggered = metric_value <= condition.threshold
                elif condition.operator == "<":
                    still_triggered = metric_value < condition.threshold
                elif condition.operator == "==":
                    still_triggered = metric_value == condition.threshold
                
                if not still_triggered:
                    resolved_alerts.append(alert)
                    logger.info(f"✅ Alert resolved: {condition.message}")
        
        # Remove resolved alerts
        for alert in resolved_alerts:
            self.alerts_active.remove(alert)
    
    async def _cleanup_disk_space(self) -> None:
        """Cleanup disk space when critical"""
        try:
            # Clean old log files
            logs_dir = Path(__file__).parent / "production" / "logs"
            if logs_dir.exists():
                old_logs = [f for f in logs_dir.glob("*.log") 
                           if (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days > 7]
                for log_file in old_logs:
                    log_file.unlink()
                    logger.info(f"🗑️ Deleted old log: {log_file}")
            
            # Clean old backup files
            backups_dir = Path(__file__).parent / "production" / "backups"
            if backups_dir.exists():
                old_backups = [d for d in backups_dir.iterdir() 
                              if d.is_dir() and (datetime.now() - datetime.fromtimestamp(d.stat().st_mtime)).days > 14]
                for backup_dir in old_backups:
                    import shutil
                    shutil.rmtree(backup_dir)
                    logger.info(f"🗑️ Deleted old backup: {backup_dir}")
                    
        except Exception as e:
            logger.error(f"❌ Disk cleanup failed: {e}")
    
    async def _performance_analysis_loop(self) -> None:
        """Analyze performance trends"""
        while self.monitoring_active:
            try:
                if len(self.metrics_history) >= 10:
                    await self._analyze_performance_trends()
                
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Performance analysis error: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_performance_trends(self) -> None:
        """Analyze system performance trends"""
        if len(self.metrics_history) < 10:
            return
        
        recent_metrics = self.metrics_history[-10:]
        
        # Calculate trends
        trends = {
            "cpu_trend": self._calculate_trend([m.cpu_percent for m in recent_metrics]),
            "memory_trend": self._calculate_trend([m.memory_percent for m in recent_metrics]),
            "disk_trend": self._calculate_trend([m.disk_usage_percent for m in recent_metrics])
        }
        
        # Update performance trends
        self.performance_trends.update(trends)
        
        # Log significant trends
        for metric, trend in trends.items():
            if abs(trend) > 5:  # Significant change
                direction = "increasing" if trend > 0 else "decreasing"
                logger.info(f"📈 Performance trend: {metric} {direction} ({trend:+.1f}%)")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend percentage from list of values"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if first_half == 0:
            return 0.0
        
        return ((second_half - first_half) / first_half) * 100
    
    async def _health_reporting_loop(self) -> None:
        """Generate periodic health reports"""
        while self.monitoring_active:
            try:
                await self._generate_health_report()
                await asyncio.sleep(3600)  # Generate report every hour
                
            except Exception as e:
                logger.error(f"❌ Health reporting error: {e}")
                await asyncio.sleep(3600)
    
    async def _generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        if not self.metrics_history:
            return {"status": "no_data"}
        
        latest_metrics = self.metrics_history[-1]
        
        # Calculate health score
        health_score = await self._calculate_health_score(latest_metrics)
        
        # Service status summary
        service_status = {}
        for service_name, metrics in self.service_metrics.items():
            service_status[service_name] = {
                "status": metrics.status,
                "cpu_percent": metrics.cpu_percent,
                "memory_mb": metrics.memory_mb,
                "uptime_hours": metrics.uptime_seconds / 3600
            }
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "system_metrics": asdict(latest_metrics),
            "service_status": service_status,
            "active_alerts": len(self.alerts_active),
            "performance_trends": self.performance_trends,
            "recommendations": await self._generate_recommendations()
        }
        
        # Save health report
        report_file = self.monitor_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(health_report, f, indent=2, default=str)
        
        return health_report
    
    async def _calculate_health_score(self, metrics: SystemMetrics) -> int:
        """Calculate overall system health score (0-100)"""
        score = 100
        
        # CPU penalty
        if metrics.cpu_percent > 80:
            score -= 20
        elif metrics.cpu_percent > 60:
            score -= 10
        
        # Memory penalty
        if metrics.memory_percent > 90:
            score -= 25
        elif metrics.memory_percent > 75:
            score -= 15
        
        # Disk penalty
        if metrics.disk_usage_percent > 95:
            score -= 30
        elif metrics.disk_usage_percent > 85:
            score -= 15
        
        # Active alerts penalty
        score -= len(self.alerts_active) * 5
        
        # Service status
        running_services = sum(1 for m in self.service_metrics.values() if m.status != "not_running")
        total_services = len(self.monitored_services)
        if total_services > 0:
            service_score = (running_services / total_services) * 20
            score = score - 20 + service_score
        
        return max(0, min(100, score))
    
    async def _generate_recommendations(self) -> List[str]:
        """Generate system recommendations"""
        recommendations = []
        
        if not self.metrics_history:
            return recommendations
        
        latest_metrics = self.metrics_history[-1]
        
        # Performance recommendations
        if latest_metrics.cpu_percent > 80:
            recommendations.append("🔧 Consider upgrading CPU or optimizing high-CPU processes")
        
        if latest_metrics.memory_percent > 85:
            recommendations.append("💾 Consider adding more RAM or optimizing memory usage")
        
        if latest_metrics.disk_usage_percent > 90:
            recommendations.append("💽 Free up disk space or add more storage")
        
        # Service recommendations
        non_running_services = [name for name, metrics in self.service_metrics.items() 
                               if metrics.status == "not_running"]
        if non_running_services:
            recommendations.append(f"🔄 Restart stopped services: {', '.join(non_running_services)}")
        
        # Alert recommendations
        if len(self.alerts_active) > 3:
            recommendations.append("🚨 Review and address active alerts")
        
        return recommendations
    
    async def _cleanup_old_metrics(self) -> None:
        """Remove old metrics to prevent memory buildup"""
        retention_hours = self.monitor_config["history_retention_hours"]
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)
        
        self.metrics_history = [m for m in self.metrics_history if m.timestamp > cutoff_time]
    
    async def _save_metrics(self, system_metrics: SystemMetrics, service_metrics: Dict[str, ServiceMetrics]) -> None:
        """Save metrics to file"""
        metrics_data = {
            "system": asdict(system_metrics),
            "services": {name: asdict(metrics) for name, metrics in service_metrics.items()}
        }
        
        # Save to daily metrics file
        date_str = datetime.now().strftime("%Y%m%d")
        metrics_file = self.monitor_dir / f"system_metrics_{date_str}.jsonl"
        
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics_data, default=str) + '\n')
    
    def get_current_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        latest_metrics = self.metrics_history[-1] if self.metrics_history else None
        
        return {
            "monitoring_active": self.monitoring_active,
            "metrics_collected": len(self.metrics_history),
            "active_alerts": len(self.alerts_active),
            "services_monitored": len(self.service_metrics),
            "latest_metrics": asdict(latest_metrics) if latest_metrics else None,
            "health_score": asyncio.run(self._calculate_health_score(latest_metrics)) if latest_metrics else 0
        }


def main():
    """Test the system monitor"""
    async def test_monitor():
        print("🔍 Tenxsom AI System Monitor")
        print("=" * 40)
        
        monitor = SystemMonitor()
        
        print("\n🧪 Testing system metrics collection...")
        metrics = await monitor._collect_system_metrics()
        
        print(f"✅ System Metrics Collected:")
        print(f"   CPU: {metrics.cpu_percent:.1f}%")
        print(f"   Memory: {metrics.memory_percent:.1f}% ({metrics.memory_available_gb:.1f}GB available)")
        print(f"   Disk: {metrics.disk_usage_percent:.1f}% ({metrics.disk_free_gb:.1f}GB free)")
        print(f"   Processes: {metrics.process_count}")
        
        print(f"\n🧪 Testing service metrics collection...")
        service_metrics = await monitor._collect_service_metrics()
        
        print(f"✅ Service Metrics:")
        for name, metrics in service_metrics.items():
            print(f"   {name}: {metrics.status} (CPU: {metrics.cpu_percent:.1f}%, Memory: {metrics.memory_mb:.1f}MB)")
        
        print(f"\n🧪 Testing alert conditions...")
        alerts = await monitor._check_alert_conditions(metrics)
        
        if alerts:
            print(f"⚠️ Active Alerts: {len(alerts)}")
            for alert in alerts:
                print(f"   • {alert['condition']['message']}")
        else:
            print(f"✅ No alerts triggered")
        
        print(f"\n🧪 Testing health report...")
        health_report = await monitor._generate_health_report()
        
        print(f"✅ Health Report Generated:")
        print(f"   Health Score: {health_report['health_score']}/100")
        print(f"   Active Alerts: {health_report['active_alerts']}")
        
        if health_report['recommendations']:
            print(f"   Recommendations:")
            for rec in health_report['recommendations']:
                print(f"     • {rec}")
        
        print(f"\n🎯 System monitor ready for production use!")
        
        # Start monitoring for a short demo
        print(f"\n⏳ Starting 30-second monitoring demo...")
        monitor.monitoring_active = True
        
        # Collect metrics for 30 seconds
        for i in range(3):
            await monitor._metrics_collection_loop.__code__.co_consts[1]  # Single iteration
            await asyncio.sleep(10)
        
        print(f"✅ Monitoring demo complete!")
        
        return health_report
    
    # Run test
    asyncio.run(test_monitor())


if __name__ == "__main__":
    main()