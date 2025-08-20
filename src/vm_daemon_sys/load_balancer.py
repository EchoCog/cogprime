"""
Load Balancer for VM-Daemon-Sys

Provides intelligent load balancing across cognitive service instances.
"""

import random
import threading
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

from .service_manager import ServiceManager, ServiceType, ServiceStatus

logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    LEAST_RESPONSE_TIME = "least_response_time"
    COGNITIVE_AWARE = "cognitive_aware"  # Custom strategy for cognitive workloads

@dataclass
class ServiceMetrics:
    """Metrics for a service instance."""
    instance_id: str
    current_connections: int = 0
    total_requests: int = 0
    average_response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    cognitive_load: float = 0.0  # Custom metric for cognitive processing
    error_rate: float = 0.0
    last_updated: float = 0.0

class LoadBalancer:
    """Intelligent load balancer for cognitive services."""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN,
                 service_manager: Optional[ServiceManager] = None):
        self.strategy = strategy
        self.service_manager = service_manager
        self.metrics: Dict[str, ServiceMetrics] = {}
        self.round_robin_counters: Dict[ServiceType, int] = {}
        self.weights: Dict[str, float] = {}
        self.lock = threading.RLock()
        
        # Initialize round robin counters
        for service_type in ServiceType:
            self.round_robin_counters[service_type] = 0
    
    def select_service_instance(self, service_type: ServiceType, 
                              request_context: Optional[Dict] = None) -> Optional[str]:
        """Select the best service instance for a request."""
        with self.lock:
            if not self.service_manager:
                logger.error("Service manager not available")
                return None
            
            # Get healthy instances
            healthy_instances = self.service_manager.get_healthy_services(service_type)
            
            if not healthy_instances:
                logger.warning(f"No healthy instances available for {service_type.value}")
                return None
            
            if len(healthy_instances) == 1:
                return healthy_instances[0].config.instance_id
            
            # Apply load balancing strategy
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_select(service_type, healthy_instances)
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_select(service_type, healthy_instances)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_select(healthy_instances)
            elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                return self._least_response_time_select(healthy_instances)
            elif self.strategy == LoadBalancingStrategy.COGNITIVE_AWARE:
                return self._cognitive_aware_select(healthy_instances, request_context)
            else:
                # Default to round robin
                return self._round_robin_select(service_type, healthy_instances)
    
    def update_service_metrics(self, instance_id: str, metrics: Dict):
        """Update metrics for a service instance."""
        with self.lock:
            current_time = time.time()
            
            if instance_id not in self.metrics:
                self.metrics[instance_id] = ServiceMetrics(instance_id=instance_id)
            
            service_metrics = self.metrics[instance_id]
            
            # Update metrics
            service_metrics.current_connections = metrics.get('connections', 0)
            service_metrics.total_requests = metrics.get('total_requests', 0)
            service_metrics.average_response_time = metrics.get('avg_response_time', 0.0)
            service_metrics.cpu_usage = metrics.get('cpu_usage', 0.0)
            service_metrics.memory_usage = metrics.get('memory_usage', 0.0)
            service_metrics.cognitive_load = metrics.get('cognitive_load', 0.0)
            service_metrics.error_rate = metrics.get('error_rate', 0.0)
            service_metrics.last_updated = current_time
    
    def record_request_start(self, instance_id: str):
        """Record the start of a request to an instance."""
        with self.lock:
            if instance_id not in self.metrics:
                self.metrics[instance_id] = ServiceMetrics(instance_id=instance_id)
            
            self.metrics[instance_id].current_connections += 1
    
    def record_request_end(self, instance_id: str, response_time: float, success: bool = True):
        """Record the completion of a request."""
        with self.lock:
            if instance_id not in self.metrics:
                return
            
            metrics = self.metrics[instance_id]
            metrics.current_connections = max(0, metrics.current_connections - 1)
            metrics.total_requests += 1
            
            # Update average response time (exponential moving average)
            alpha = 0.1  # Smoothing factor
            metrics.average_response_time = (
                alpha * response_time + 
                (1 - alpha) * metrics.average_response_time
            )
            
            # Update error rate
            if not success:
                metrics.error_rate = alpha * 1.0 + (1 - alpha) * metrics.error_rate
            else:
                metrics.error_rate = (1 - alpha) * metrics.error_rate
    
    def update_service_weights(self):
        """Update service weights based on current metrics."""
        with self.lock:
            current_time = time.time()
            
            for instance_id, metrics in self.metrics.items():
                # Skip stale metrics
                if current_time - metrics.last_updated > 300:  # 5 minutes
                    continue
                
                # Calculate weight based on performance
                weight = self._calculate_instance_weight(metrics)
                self.weights[instance_id] = weight
    
    def get_service_metrics(self, instance_id: str) -> Optional[ServiceMetrics]:
        """Get metrics for a service instance."""
        with self.lock:
            return self.metrics.get(instance_id)
    
    def get_load_distribution(self, service_type: ServiceType) -> Dict[str, float]:
        """Get current load distribution for a service type."""
        with self.lock:
            if not self.service_manager:
                return {}
            
            instances = self.service_manager.get_services_by_type(service_type)
            distribution = {}
            
            total_load = 0
            for instance in instances:
                instance_id = instance.config.instance_id
                if instance_id in self.metrics:
                    load = self.metrics[instance_id].current_connections
                    distribution[instance_id] = load
                    total_load += load
            
            # Normalize to percentages
            if total_load > 0:
                for instance_id in distribution:
                    distribution[instance_id] = (distribution[instance_id] / total_load) * 100
            
            return distribution
    
    def _round_robin_select(self, service_type: ServiceType, instances: List) -> str:
        """Round robin selection."""
        counter = self.round_robin_counters[service_type]
        selected = instances[counter % len(instances)]
        self.round_robin_counters[service_type] = (counter + 1) % len(instances)
        return selected.config.instance_id
    
    def _weighted_round_robin_select(self, service_type: ServiceType, instances: List) -> str:
        """Weighted round robin selection."""
        # Calculate weights for each instance
        weighted_instances = []
        
        for instance in instances:
            instance_id = instance.config.instance_id
            weight = self.weights.get(instance_id, 1.0)
            # Add instance multiple times based on weight
            count = max(1, int(weight * 10))
            weighted_instances.extend([instance] * count)
        
        if not weighted_instances:
            return instances[0].config.instance_id
        
        # Use round robin on weighted list
        counter = self.round_robin_counters[service_type]
        selected = weighted_instances[counter % len(weighted_instances)]
        self.round_robin_counters[service_type] = (counter + 1) % len(weighted_instances)
        return selected.config.instance_id
    
    def _least_connections_select(self, instances: List) -> str:
        """Select instance with least connections."""
        best_instance = None
        min_connections = float('inf')
        
        for instance in instances:
            instance_id = instance.config.instance_id
            connections = 0
            
            if instance_id in self.metrics:
                connections = self.metrics[instance_id].current_connections
            
            if connections < min_connections:
                min_connections = connections
                best_instance = instance
        
        return best_instance.config.instance_id if best_instance else instances[0].config.instance_id
    
    def _least_response_time_select(self, instances: List) -> str:
        """Select instance with least average response time."""
        best_instance = None
        min_response_time = float('inf')
        
        for instance in instances:
            instance_id = instance.config.instance_id
            response_time = float('inf')
            
            if instance_id in self.metrics:
                response_time = self.metrics[instance_id].average_response_time
                # If no response time data, use a default
                if response_time == 0:
                    response_time = 100.0  # Default 100ms
            
            if response_time < min_response_time:
                min_response_time = response_time
                best_instance = instance
        
        return best_instance.config.instance_id if best_instance else instances[0].config.instance_id
    
    def _cognitive_aware_select(self, instances: List, request_context: Optional[Dict] = None) -> str:
        """Cognitive-aware selection considering workload complexity."""
        best_instance = None
        best_score = float('inf')
        
        # Get request complexity
        request_complexity = 1.0
        if request_context:
            request_complexity = request_context.get('complexity', 1.0)
        
        for instance in instances:
            instance_id = instance.config.instance_id
            
            if instance_id not in self.metrics:
                # No metrics available, use default score
                score = request_complexity
            else:
                metrics = self.metrics[instance_id]
                
                # Calculate composite score considering multiple factors
                connection_factor = metrics.current_connections / 10.0
                response_time_factor = metrics.average_response_time / 1000.0  # Normalize to seconds
                cognitive_load_factor = metrics.cognitive_load
                error_factor = metrics.error_rate * 10.0
                
                # Weighted combination
                score = (
                    0.3 * connection_factor +
                    0.3 * response_time_factor + 
                    0.2 * cognitive_load_factor +
                    0.2 * error_factor
                ) * request_complexity
            
            if score < best_score:
                best_score = score
                best_instance = instance
        
        return best_instance.config.instance_id if best_instance else instances[0].config.instance_id
    
    def _calculate_instance_weight(self, metrics: ServiceMetrics) -> float:
        """Calculate weight for an instance based on its metrics."""
        # Higher weight means better performance
        base_weight = 1.0
        
        # Reduce weight based on current load
        connection_penalty = metrics.current_connections * 0.1
        
        # Reduce weight based on response time
        response_time_penalty = metrics.average_response_time / 1000.0  # Convert to seconds
        
        # Reduce weight based on error rate
        error_penalty = metrics.error_rate * 5.0
        
        # Reduce weight based on cognitive load
        cognitive_penalty = metrics.cognitive_load * 0.5
        
        weight = max(0.1, base_weight - connection_penalty - response_time_penalty - 
                    error_penalty - cognitive_penalty)
        
        return weight