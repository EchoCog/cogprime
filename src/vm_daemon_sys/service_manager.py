"""
Service Manager for VM-Daemon-Sys

Manages lifecycle, configuration, and coordination of cognitive services.
"""

import asyncio
import logging
import threading
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Types of cognitive services."""
    RELEVANCE = "relevance"
    WISDOM = "wisdom" 
    RATIONALITY = "rationality"
    PHENOMENOLOGY = "phenomenology"
    MEANING_MAKING = "meaning_making"
    INTEGRATION = "integration"
    SILICON_SAGE = "silicon_sage"

class ServiceStatus(Enum):
    """Status states for services."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class ServiceConfig:
    """Configuration for a cognitive service."""
    service_type: ServiceType
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    port: int = 8080
    host: str = "localhost"
    workers: int = 1
    memory_limit: int = 1024  # MB
    cpu_limit: float = 1.0    # CPU cores
    environment: Dict[str, str] = field(default_factory=dict)
    dependencies: List[ServiceType] = field(default_factory=list)
    auto_restart: bool = True
    health_check_interval: int = 30  # seconds
    startup_timeout: int = 60  # seconds
    shutdown_timeout: int = 30  # seconds

@dataclass
class ServiceInstance:
    """Represents a running service instance."""
    config: ServiceConfig
    status: ServiceStatus = ServiceStatus.STOPPED
    process_id: Optional[int] = None
    start_time: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"
    error_count: int = 0
    restart_count: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)

class ServiceManager:
    """Manages cognitive service lifecycle and coordination."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.services: Dict[str, ServiceInstance] = {}
        self.service_registry: Dict[ServiceType, List[str]] = {
            service_type: [] for service_type in ServiceType
        }
        self.status_callbacks: List[Callable[[str, ServiceStatus], None]] = []
        self.lock = threading.RLock()
        self.running = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Load configuration if provided
        if config_file:
            self.load_config(config_file)
    
    def register_service(self, config: ServiceConfig) -> str:
        """Register a new service configuration."""
        with self.lock:
            instance = ServiceInstance(config=config)
            instance_id = config.instance_id
            
            self.services[instance_id] = instance
            self.service_registry[config.service_type].append(instance_id)
            
            logger.info(f"Registered service {config.service_type.value} with ID {instance_id}")
            return instance_id
    
    def unregister_service(self, instance_id: str) -> bool:
        """Unregister a service."""
        with self.lock:
            if instance_id not in self.services:
                return False
            
            instance = self.services[instance_id]
            
            # Stop service if running
            if instance.status in [ServiceStatus.RUNNING, ServiceStatus.STARTING]:
                self.stop_service(instance_id)
            
            # Remove from registry
            service_type = instance.config.service_type
            if instance_id in self.service_registry[service_type]:
                self.service_registry[service_type].remove(instance_id)
            
            del self.services[instance_id]
            logger.info(f"Unregistered service {instance_id}")
            return True
    
    def start_service(self, instance_id: str) -> bool:
        """Start a specific service instance."""
        with self.lock:
            if instance_id not in self.services:
                logger.error(f"Service {instance_id} not found")
                return False
            
            instance = self.services[instance_id]
            
            if instance.status != ServiceStatus.STOPPED:
                logger.warning(f"Service {instance_id} is not stopped (status: {instance.status})")
                return False
            
            # Check dependencies
            if not self._check_dependencies(instance.config):
                logger.error(f"Dependencies not met for service {instance_id}")
                return False
            
            try:
                instance.status = ServiceStatus.STARTING
                instance.start_time = datetime.now()
                self._notify_status_change(instance_id, instance.status)
                
                # Here we would actually start the service process
                # For now, simulate startup
                success = self._start_service_process(instance)
                
                if success:
                    instance.status = ServiceStatus.RUNNING
                    logger.info(f"Started service {instance_id}")
                else:
                    instance.status = ServiceStatus.ERROR
                    instance.error_count += 1
                    logger.error(f"Failed to start service {instance_id}")
                
                self._notify_status_change(instance_id, instance.status)
                return success
                
            except Exception as e:
                instance.status = ServiceStatus.ERROR
                instance.error_count += 1
                logger.error(f"Exception starting service {instance_id}: {e}")
                self._notify_status_change(instance_id, instance.status)
                return False
    
    def stop_service(self, instance_id: str) -> bool:
        """Stop a specific service instance."""
        with self.lock:
            if instance_id not in self.services:
                logger.error(f"Service {instance_id} not found")
                return False
            
            instance = self.services[instance_id]
            
            if instance.status not in [ServiceStatus.RUNNING, ServiceStatus.STARTING]:
                logger.warning(f"Service {instance_id} is not running (status: {instance.status})")
                return False
            
            try:
                instance.status = ServiceStatus.STOPPING
                self._notify_status_change(instance_id, instance.status)
                
                # Here we would actually stop the service process
                success = self._stop_service_process(instance)
                
                if success:
                    instance.status = ServiceStatus.STOPPED
                    instance.process_id = None
                    logger.info(f"Stopped service {instance_id}")
                else:
                    instance.status = ServiceStatus.ERROR
                    instance.error_count += 1
                    logger.error(f"Failed to stop service {instance_id}")
                
                self._notify_status_change(instance_id, instance.status)
                return success
                
            except Exception as e:
                instance.status = ServiceStatus.ERROR
                instance.error_count += 1
                logger.error(f"Exception stopping service {instance_id}: {e}")
                self._notify_status_change(instance_id, instance.status)
                return False
    
    def restart_service(self, instance_id: str) -> bool:
        """Restart a service instance."""
        if self.stop_service(instance_id):
            time.sleep(1)  # Brief pause
            if self.start_service(instance_id):
                with self.lock:
                    self.services[instance_id].restart_count += 1
                return True
        return False
    
    def get_service_status(self, instance_id: str) -> Optional[ServiceStatus]:
        """Get the status of a service instance."""
        with self.lock:
            return self.services.get(instance_id, {}).status if instance_id in self.services else None
    
    def get_services_by_type(self, service_type: ServiceType) -> List[ServiceInstance]:
        """Get all service instances of a specific type."""
        with self.lock:
            instance_ids = self.service_registry.get(service_type, [])
            return [self.services[instance_id] for instance_id in instance_ids 
                   if instance_id in self.services]
    
    def get_healthy_services(self, service_type: ServiceType) -> List[ServiceInstance]:
        """Get all healthy running services of a specific type."""
        services = self.get_services_by_type(service_type)
        return [service for service in services 
               if service.status == ServiceStatus.RUNNING and 
               service.health_status == "healthy"]
    
    def start_monitoring(self):
        """Start the service monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self._monitor_thread = threading.Thread(target=self._monitor_services, daemon=True)
        self._monitor_thread.start()
        logger.info("Started service monitoring")
    
    def stop_monitoring(self):
        """Stop the service monitoring thread."""
        self.running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Stopped service monitoring")
    
    def add_status_callback(self, callback: Callable[[str, ServiceStatus], None]):
        """Add a callback for status changes."""
        self.status_callbacks.append(callback)
    
    def load_config(self, config_file: str):
        """Load service configurations from file."""
        # Implementation would load from YAML/JSON config file
        pass
    
    def _check_dependencies(self, config: ServiceConfig) -> bool:
        """Check if service dependencies are satisfied."""
        for dep_type in config.dependencies:
            healthy_services = self.get_healthy_services(dep_type)
            if not healthy_services:
                return False
        return True
    
    def _start_service_process(self, instance: ServiceInstance) -> bool:
        """Start the actual service process."""
        # In a real implementation, this would:
        # 1. Create appropriate command line based on service type
        # 2. Start the process with proper environment
        # 3. Set up monitoring and logging
        # 4. Store process ID
        
        # For simulation, just set a fake process ID
        instance.process_id = 12345 + hash(instance.config.instance_id) % 10000
        return True
    
    def _stop_service_process(self, instance: ServiceInstance) -> bool:
        """Stop the actual service process."""
        # In a real implementation, this would:
        # 1. Send termination signal to process
        # 2. Wait for graceful shutdown
        # 3. Force kill if necessary
        # 4. Clean up resources
        
        return True
    
    def _monitor_services(self):
        """Monitor service health and perform auto-restart if needed."""
        while self.running:
            try:
                with self.lock:
                    for instance_id, instance in self.services.items():
                        if instance.status == ServiceStatus.RUNNING:
                            # Perform health check
                            is_healthy = self._health_check(instance)
                            
                            if not is_healthy:
                                instance.error_count += 1
                                instance.health_status = "unhealthy"
                                
                                # Auto-restart if configured and error count is reasonable
                                if (instance.config.auto_restart and 
                                    instance.error_count < 5):
                                    logger.warning(f"Auto-restarting unhealthy service {instance_id}")
                                    threading.Thread(
                                        target=self.restart_service, 
                                        args=(instance_id,), 
                                        daemon=True
                                    ).start()
                            else:
                                instance.health_status = "healthy"
                                instance.error_count = max(0, instance.error_count - 1)
                            
                            instance.last_health_check = datetime.now()
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in service monitoring: {e}")
                time.sleep(5)
    
    def _health_check(self, instance: ServiceInstance) -> bool:
        """Perform health check on a service instance."""
        # In a real implementation, this would:
        # 1. Check if process is still running
        # 2. Make HTTP health check request
        # 3. Verify resource usage is within limits
        # 4. Check response time
        
        # For simulation, randomly return health status
        import random
        return random.random() > 0.1  # 90% healthy
    
    def _notify_status_change(self, instance_id: str, status: ServiceStatus):
        """Notify registered callbacks of status changes."""
        for callback in self.status_callbacks:
            try:
                callback(instance_id, status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")