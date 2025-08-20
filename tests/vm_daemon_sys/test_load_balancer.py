"""
Tests for VM-Daemon-Sys load balancer.
"""

import unittest
from unittest.mock import Mock, MagicMock
from src.vm_daemon_sys.load_balancer import (
    LoadBalancer, LoadBalancingStrategy, ServiceMetrics
)
from src.vm_daemon_sys.service_manager import (
    ServiceManager, ServiceConfig, ServiceType, ServiceStatus, ServiceInstance
)

class TestLoadBalancer(unittest.TestCase):
    """Test cases for LoadBalancer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service_manager = Mock(spec=ServiceManager)
        self.load_balancer = LoadBalancer(
            strategy=LoadBalancingStrategy.ROUND_ROBIN,
            service_manager=self.service_manager
        )
    
    def test_round_robin_selection(self):
        """Test round robin load balancing."""
        # Mock healthy instances
        instances = [
            self._create_mock_instance("instance_1", ServiceType.RELEVANCE),
            self._create_mock_instance("instance_2", ServiceType.RELEVANCE),
            self._create_mock_instance("instance_3", ServiceType.RELEVANCE)
        ]
        
        self.service_manager.get_healthy_services.return_value = instances
        
        # Test round robin behavior
        selections = []
        for _ in range(6):  # Two full rounds
            selected = self.load_balancer.select_service_instance(ServiceType.RELEVANCE)
            selections.append(selected)
        
        expected = ["instance_1", "instance_2", "instance_3", "instance_1", "instance_2", "instance_3"]
        self.assertEqual(selections, expected)
    
    def test_least_connections_selection(self):
        """Test least connections load balancing."""
        self.load_balancer.strategy = LoadBalancingStrategy.LEAST_CONNECTIONS
        
        # Mock instances with different connection counts
        instances = [
            self._create_mock_instance("instance_1", ServiceType.WISDOM),
            self._create_mock_instance("instance_2", ServiceType.WISDOM),
            self._create_mock_instance("instance_3", ServiceType.WISDOM)
        ]
        
        self.service_manager.get_healthy_services.return_value = instances
        
        # Set up metrics with different connection counts
        self.load_balancer.metrics = {
            "instance_1": ServiceMetrics("instance_1", current_connections=5),
            "instance_2": ServiceMetrics("instance_2", current_connections=2),
            "instance_3": ServiceMetrics("instance_3", current_connections=8)
        }
        
        selected = self.load_balancer.select_service_instance(ServiceType.WISDOM)
        self.assertEqual(selected, "instance_2")  # Least connections
    
    def test_cognitive_aware_selection(self):
        """Test cognitive-aware load balancing."""
        self.load_balancer.strategy = LoadBalancingStrategy.COGNITIVE_AWARE
        
        instances = [
            self._create_mock_instance("instance_1", ServiceType.INTEGRATION),
            self._create_mock_instance("instance_2", ServiceType.INTEGRATION)
        ]
        
        self.service_manager.get_healthy_services.return_value = instances
        
        # Set up metrics favoring instance_2
        self.load_balancer.metrics = {
            "instance_1": ServiceMetrics(
                "instance_1", 
                current_connections=10,
                average_response_time=500.0,
                cognitive_load=0.8,
                error_rate=0.05
            ),
            "instance_2": ServiceMetrics(
                "instance_2",
                current_connections=3,
                average_response_time=100.0,
                cognitive_load=0.3,
                error_rate=0.01
            )
        }
        
        # Test with high complexity request
        context = {"complexity": 0.9}
        selected = self.load_balancer.select_service_instance(ServiceType.INTEGRATION, context)
        self.assertEqual(selected, "instance_2")  # Better performing instance
    
    def test_update_service_metrics(self):
        """Test updating service metrics."""
        metrics_data = {
            'connections': 5,
            'total_requests': 100,
            'avg_response_time': 150.0,
            'cpu_usage': 65.5,
            'memory_usage': 70.2,
            'cognitive_load': 0.6,
            'error_rate': 0.02
        }
        
        self.load_balancer.update_service_metrics("test_instance", metrics_data)
        
        metrics = self.load_balancer.metrics["test_instance"]
        self.assertEqual(metrics.current_connections, 5)
        self.assertEqual(metrics.total_requests, 100)
        self.assertEqual(metrics.average_response_time, 150.0)
        self.assertEqual(metrics.cognitive_load, 0.6)
    
    def test_record_request_lifecycle(self):
        """Test recording request start and end."""
        instance_id = "test_instance"
        
        # Record request start
        self.load_balancer.record_request_start(instance_id)
        metrics = self.load_balancer.metrics[instance_id]
        self.assertEqual(metrics.current_connections, 1)
        
        # Record successful request end
        self.load_balancer.record_request_end(instance_id, 200.0, success=True)
        self.assertEqual(metrics.current_connections, 0)
        self.assertEqual(metrics.total_requests, 1)
        self.assertAlmostEqual(metrics.average_response_time, 20.0, places=1)  # Exponential moving average
    
    def test_no_healthy_instances(self):
        """Test behavior when no healthy instances are available."""
        self.service_manager.get_healthy_services.return_value = []
        
        selected = self.load_balancer.select_service_instance(ServiceType.RATIONALITY)
        self.assertIsNone(selected)
    
    def test_single_instance(self):
        """Test behavior with single instance."""
        instance = self._create_mock_instance("only_instance", ServiceType.PHENOMENOLOGY)
        self.service_manager.get_healthy_services.return_value = [instance]
        
        selected = self.load_balancer.select_service_instance(ServiceType.PHENOMENOLOGY)
        self.assertEqual(selected, "only_instance")
    
    def test_weight_calculation(self):
        """Test service weight calculation."""
        metrics = ServiceMetrics(
            "test_instance",
            current_connections=5,
            average_response_time=200.0,
            error_rate=0.03,
            cognitive_load=0.5
        )
        
        weight = self.load_balancer._calculate_instance_weight(metrics)
        
        # Weight should be positive and less than 1.0 due to penalties
        self.assertGreater(weight, 0.0)
        self.assertLess(weight, 1.0)
    
    def test_load_distribution(self):
        """Test getting load distribution."""
        instances = [
            self._create_mock_instance("instance_1", ServiceType.MEANING_MAKING),
            self._create_mock_instance("instance_2", ServiceType.MEANING_MAKING)
        ]
        
        self.service_manager.get_services_by_type.return_value = instances
        
        # Set up metrics
        self.load_balancer.metrics = {
            "instance_1": ServiceMetrics("instance_1", current_connections=8),
            "instance_2": ServiceMetrics("instance_2", current_connections=2)
        }
        
        distribution = self.load_balancer.get_load_distribution(ServiceType.MEANING_MAKING)
        
        self.assertAlmostEqual(distribution["instance_1"], 80.0, places=1)
        self.assertAlmostEqual(distribution["instance_2"], 20.0, places=1)
    
    def _create_mock_instance(self, instance_id: str, service_type: ServiceType):
        """Create a mock service instance."""
        config = ServiceConfig(service_type=service_type, instance_id=instance_id)
        instance = ServiceInstance(config=config, status=ServiceStatus.RUNNING)
        return instance

if __name__ == '__main__':
    unittest.main()