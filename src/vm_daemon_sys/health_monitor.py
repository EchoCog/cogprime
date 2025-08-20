"""
Health Monitor for VM-Daemon-Sys

Monitors the health and performance of cognitive services.
"""

import threading
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from .service_manager import ServiceManager, ServiceType, ServiceStatus

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class HealthMetric:
    """Individual health metric."""
    name: str
    value: float
    threshold_warning: float
    threshold_critical: float
    unit: str = ""
    description: str = ""

@dataclass
class HealthReport:
    """Health report for a service or system."""
    status: HealthStatus
    metrics: List[HealthMetric] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

class HealthMonitor:
    """Monitors health and performance of cognitive services."""
    
    def __init__(self, service_manager: ServiceManager, check_interval: int = 60):
        self.service_manager = service_manager
        self.check_interval = check_interval
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Health reports cache
        self.service_reports: Dict[str, HealthReport] = {}
        self.system_report: Optional[HealthReport] = None
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[str, HealthStatus, HealthReport], None]] = []
        
        # Thresholds
        self.thresholds = {
            'cpu_usage': {'warning': 70.0, 'critical': 90.0},
            'memory_usage': {'warning': 80.0, 'critical': 95.0},
            'response_time': {'warning': 1000.0, 'critical': 5000.0},  # milliseconds
            'error_rate': {'warning': 0.05, 'critical': 0.1},  # 5% and 10%
            'connection_count': {'warning': 100, 'critical': 200},
            'cognitive_load': {'warning': 0.8, 'critical': 0.95}
        }
        
        self.lock = threading.RLock()
    
    def start(self):
        """Start health monitoring."""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health monitoring started")
    
    def stop(self):
        """Stop health monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")
    
    def get_service_health(self, instance_id: str) -> Optional[HealthReport]:
        """Get health report for a specific service instance."""
        with self.lock:
            return self.service_reports.get(instance_id)
    
    def get_system_health(self) -> HealthReport:
        """Get overall system health report."""
        with self.lock:
            if self.system_report is None:
                return HealthReport(status=HealthStatus.UNKNOWN)
            return self.system_report
    
    def get_service_type_health(self, service_type: ServiceType) -> HealthReport:
        """Get aggregated health for all instances of a service type."""
        instances = self.service_manager.get_services_by_type(service_type)
        
        if not instances:
            return HealthReport(
                status=HealthStatus.UNKNOWN,
                issues=[f"No instances found for {service_type.value}"]
            )
        
        # Aggregate health across instances
        all_metrics = []
        all_issues = []
        worst_status = HealthStatus.HEALTHY
        
        for instance in instances:
            instance_id = instance.config.instance_id
            report = self.get_service_health(instance_id)
            
            if report:
                all_metrics.extend(report.metrics)
                all_issues.extend([f"{instance_id}: {issue}" for issue in report.issues])
                
                # Track worst status
                if report.status == HealthStatus.CRITICAL:
                    worst_status = HealthStatus.CRITICAL
                elif report.status == HealthStatus.WARNING and worst_status != HealthStatus.CRITICAL:
                    worst_status = HealthStatus.WARNING
        
        return HealthReport(
            status=worst_status,
            metrics=all_metrics,
            issues=all_issues
        )
    
    def add_alert_callback(self, callback: Callable[[str, HealthStatus, HealthReport], None]):
        """Add a callback for health alerts."""
        self.alert_callbacks.append(callback)
    
    def set_threshold(self, metric_name: str, warning: float, critical: float):
        """Set custom thresholds for a metric."""
        self.thresholds[metric_name] = {
            'warning': warning,
            'critical': critical
        }
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self._perform_health_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(5)
    
    def _perform_health_checks(self):
        """Perform health checks on all services."""
        with self.lock:
            # Check individual services
            for instance_id, instance in self.service_manager.services.items():
                if instance.status == ServiceStatus.RUNNING:
                    report = self._check_service_health(instance_id, instance)
                    
                    # Store report
                    old_status = self.service_reports.get(instance_id, HealthReport(HealthStatus.UNKNOWN)).status
                    self.service_reports[instance_id] = report
                    
                    # Send alerts if status changed to warning or critical
                    if (report.status in [HealthStatus.WARNING, HealthStatus.CRITICAL] and 
                        old_status != report.status):
                        self._send_alerts(instance_id, report.status, report)
            
            # Update system health
            self._update_system_health()
    
    def _check_service_health(self, instance_id: str, instance) -> HealthReport:
        """Check health of a specific service instance."""
        metrics = []
        issues = []
        recommendations = []
        overall_status = HealthStatus.HEALTHY
        
        try:
            # Simulate getting metrics (in real implementation, this would query the service)
            service_metrics = self._get_service_metrics(instance_id)
            
            # Check CPU usage
            cpu_metric = HealthMetric(
                name="cpu_usage",
                value=service_metrics.get('cpu_usage', 0),
                threshold_warning=self.thresholds['cpu_usage']['warning'],
                threshold_critical=self.thresholds['cpu_usage']['critical'],
                unit="%",
                description="CPU utilization"
            )
            metrics.append(cpu_metric)
            
            status = self._evaluate_metric_status(cpu_metric)
            if status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                issues.append(f"High CPU usage: {cpu_metric.value:.1f}%")
                recommendations.append("Consider scaling up or optimizing CPU-intensive operations")
            elif status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.WARNING
                issues.append(f"Elevated CPU usage: {cpu_metric.value:.1f}%")
            
            # Check memory usage
            memory_metric = HealthMetric(
                name="memory_usage",
                value=service_metrics.get('memory_usage', 0),
                threshold_warning=self.thresholds['memory_usage']['warning'],
                threshold_critical=self.thresholds['memory_usage']['critical'],
                unit="%",
                description="Memory utilization"
            )
            metrics.append(memory_metric)
            
            status = self._evaluate_metric_status(memory_metric)
            if status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                issues.append(f"High memory usage: {memory_metric.value:.1f}%")
                recommendations.append("Consider increasing memory allocation or optimizing memory usage")
            elif status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.WARNING
                issues.append(f"Elevated memory usage: {memory_metric.value:.1f}%")
            
            # Check response time
            response_time_metric = HealthMetric(
                name="response_time",
                value=service_metrics.get('avg_response_time', 0),
                threshold_warning=self.thresholds['response_time']['warning'],
                threshold_critical=self.thresholds['response_time']['critical'],
                unit="ms",
                description="Average response time"
            )
            metrics.append(response_time_metric)
            
            status = self._evaluate_metric_status(response_time_metric)
            if status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                issues.append(f"High response time: {response_time_metric.value:.1f}ms")
                recommendations.append("Investigate performance bottlenecks or scale horizontally")
            elif status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.WARNING
                issues.append(f"Elevated response time: {response_time_metric.value:.1f}ms")
            
            # Check error rate
            error_rate_metric = HealthMetric(
                name="error_rate",
                value=service_metrics.get('error_rate', 0),
                threshold_warning=self.thresholds['error_rate']['warning'],
                threshold_critical=self.thresholds['error_rate']['critical'],
                unit="%",
                description="Error rate"
            )
            metrics.append(error_rate_metric)
            
            status = self._evaluate_metric_status(error_rate_metric)
            if status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                issues.append(f"High error rate: {error_rate_metric.value:.2%}")
                recommendations.append("Investigate error causes and implement fixes")
            elif status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.WARNING
                issues.append(f"Elevated error rate: {error_rate_metric.value:.2%}")
            
            # Check cognitive load (custom metric)
            cognitive_load_metric = HealthMetric(
                name="cognitive_load",
                value=service_metrics.get('cognitive_load', 0),
                threshold_warning=self.thresholds['cognitive_load']['warning'],
                threshold_critical=self.thresholds['cognitive_load']['critical'],
                unit="",
                description="Cognitive processing load"
            )
            metrics.append(cognitive_load_metric)
            
            status = self._evaluate_metric_status(cognitive_load_metric)
            if status == HealthStatus.CRITICAL:
                overall_status = HealthStatus.CRITICAL
                issues.append(f"High cognitive load: {cognitive_load_metric.value:.2f}")
                recommendations.append("Reduce cognitive complexity or add more processing capacity")
            elif status == HealthStatus.WARNING and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.WARNING
                issues.append(f"Elevated cognitive load: {cognitive_load_metric.value:.2f}")
            
        except Exception as e:
            logger.error(f"Error checking health for {instance_id}: {e}")
            overall_status = HealthStatus.UNKNOWN
            issues.append(f"Health check failed: {str(e)}")
        
        return HealthReport(
            status=overall_status,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations
        )
    
    def _get_service_metrics(self, instance_id: str) -> Dict:
        """Get metrics for a service instance."""
        # In a real implementation, this would query the actual service
        # For simulation, return some sample metrics
        import random
        
        return {
            'cpu_usage': random.uniform(10, 95),
            'memory_usage': random.uniform(20, 90),
            'avg_response_time': random.uniform(50, 2000),
            'error_rate': random.uniform(0, 0.15),
            'cognitive_load': random.uniform(0.1, 1.0),
            'connections': random.randint(0, 150)
        }
    
    def _evaluate_metric_status(self, metric: HealthMetric) -> HealthStatus:
        """Evaluate the status of a metric based on thresholds."""
        if metric.value >= metric.threshold_critical:
            return HealthStatus.CRITICAL
        elif metric.value >= metric.threshold_warning:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def _update_system_health(self):
        """Update overall system health based on service health."""
        if not self.service_reports:
            self.system_report = HealthReport(status=HealthStatus.UNKNOWN)
            return
        
        # Count services by status
        status_counts = {status: 0 for status in HealthStatus}
        total_services = len(self.service_reports)
        
        for report in self.service_reports.values():
            status_counts[report.status] += 1
        
        # Determine overall status
        if status_counts[HealthStatus.CRITICAL] > 0:
            overall_status = HealthStatus.CRITICAL
        elif status_counts[HealthStatus.WARNING] > 0:
            overall_status = HealthStatus.WARNING
        elif status_counts[HealthStatus.UNKNOWN] == total_services:
            overall_status = HealthStatus.UNKNOWN
        else:
            overall_status = HealthStatus.HEALTHY
        
        # Create system metrics
        system_metrics = [
            HealthMetric(
                name="services_healthy",
                value=status_counts[HealthStatus.HEALTHY],
                threshold_warning=total_services * 0.8,
                threshold_critical=total_services * 0.6,
                unit="count",
                description="Number of healthy services"
            ),
            HealthMetric(
                name="services_warning",
                value=status_counts[HealthStatus.WARNING],
                threshold_warning=total_services * 0.2,
                threshold_critical=total_services * 0.4,
                unit="count",
                description="Number of services with warnings"
            ),
            HealthMetric(
                name="services_critical",
                value=status_counts[HealthStatus.CRITICAL],
                threshold_warning=1,
                threshold_critical=total_services * 0.3,
                unit="count",
                description="Number of critical services"
            )
        ]
        
        # Create issues and recommendations
        issues = []
        recommendations = []
        
        if status_counts[HealthStatus.CRITICAL] > 0:
            issues.append(f"{status_counts[HealthStatus.CRITICAL]} services in critical state")
            recommendations.append("Immediately investigate critical services")
        
        if status_counts[HealthStatus.WARNING] > 0:
            issues.append(f"{status_counts[HealthStatus.WARNING]} services with warnings")
            recommendations.append("Monitor warning services closely")
        
        self.system_report = HealthReport(
            status=overall_status,
            metrics=system_metrics,
            issues=issues,
            recommendations=recommendations
        )
    
    def _send_alerts(self, service_id: str, status: HealthStatus, report: HealthReport):
        """Send alerts to registered callbacks."""
        for callback in self.alert_callbacks:
            try:
                callback(service_id, status, report)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")