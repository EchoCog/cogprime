"""
VM-Daemon-Sys: Service orchestration system for Silicon-Sage cognitive architecture.

This module provides distributed service management, load balancing, health monitoring,
and coordination for the various cognitive components of the CogPrime system.
"""

from .daemon import CognitiveDaemon
from .service_manager import ServiceManager, ServiceType, ServiceStatus
from .load_balancer import LoadBalancer, LoadBalancingStrategy
from .health_monitor import HealthMonitor, HealthStatus
from .orchestrator import CognitiveOrchestrator

__version__ = "1.0.0"
__all__ = [
    "CognitiveDaemon",
    "ServiceManager", 
    "ServiceType",
    "ServiceStatus",
    "LoadBalancer",
    "LoadBalancingStrategy", 
    "HealthMonitor",
    "HealthStatus",
    "CognitiveOrchestrator"
]