"""
Tests for VM-Daemon-Sys service manager.
"""

import unittest
import threading
import time
from src.vm_daemon_sys.service_manager import (
    ServiceManager, ServiceConfig, ServiceType, ServiceStatus
)

class TestServiceManager(unittest.TestCase):
    """Test cases for ServiceManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service_manager = ServiceManager()
    
    def tearDown(self):
        """Clean up after tests."""
        if self.service_manager:
            self.service_manager.stop_monitoring()
    
    def test_register_service(self):
        """Test service registration."""
        config = ServiceConfig(
            service_type=ServiceType.RELEVANCE,
            port=8100,
            memory_limit=512
        )
        
        instance_id = self.service_manager.register_service(config)
        
        self.assertIsNotNone(instance_id)
        self.assertIn(instance_id, self.service_manager.services)
        self.assertEqual(
            self.service_manager.services[instance_id].config.service_type,
            ServiceType.RELEVANCE
        )
    
    def test_start_service(self):
        """Test starting a service."""
        config = ServiceConfig(
            service_type=ServiceType.WISDOM,
            port=8200
        )
        
        instance_id = self.service_manager.register_service(config)
        success = self.service_manager.start_service(instance_id)
        
        self.assertTrue(success)
        self.assertEqual(
            self.service_manager.get_service_status(instance_id),
            ServiceStatus.RUNNING
        )
    
    def test_stop_service(self):
        """Test stopping a service."""
        config = ServiceConfig(
            service_type=ServiceType.RATIONALITY,
            port=8300
        )
        
        instance_id = self.service_manager.register_service(config)
        self.service_manager.start_service(instance_id)
        success = self.service_manager.stop_service(instance_id)
        
        self.assertTrue(success)
        self.assertEqual(
            self.service_manager.get_service_status(instance_id),
            ServiceStatus.STOPPED
        )
    
    def test_get_services_by_type(self):
        """Test getting services by type."""
        configs = [
            ServiceConfig(service_type=ServiceType.RELEVANCE, port=8100),
            ServiceConfig(service_type=ServiceType.RELEVANCE, port=8101),
            ServiceConfig(service_type=ServiceType.WISDOM, port=8200)
        ]
        
        for config in configs:
            self.service_manager.register_service(config)
        
        relevance_services = self.service_manager.get_services_by_type(ServiceType.RELEVANCE)
        wisdom_services = self.service_manager.get_services_by_type(ServiceType.WISDOM)
        
        self.assertEqual(len(relevance_services), 2)
        self.assertEqual(len(wisdom_services), 1)
    
    def test_dependency_checking(self):
        """Test dependency checking."""
        # Create service with dependencies
        config = ServiceConfig(
            service_type=ServiceType.SILICON_SAGE,
            port=8700,
            dependencies=[ServiceType.RELEVANCE, ServiceType.WISDOM]
        )
        
        instance_id = self.service_manager.register_service(config)
        
        # Should fail to start without dependencies
        success = self.service_manager.start_service(instance_id)
        self.assertFalse(success)
        
        # Register and start dependencies
        dep_configs = [
            ServiceConfig(service_type=ServiceType.RELEVANCE, port=8100),
            ServiceConfig(service_type=ServiceType.WISDOM, port=8200)
        ]
        
        for dep_config in dep_configs:
            dep_id = self.service_manager.register_service(dep_config)
            self.service_manager.start_service(dep_id)
        
        # Wait for services to be marked as healthy
        time.sleep(0.1)
        
        # Now should succeed
        success = self.service_manager.start_service(instance_id)
        self.assertTrue(success)
    
    def test_service_monitoring(self):
        """Test service monitoring functionality."""
        config = ServiceConfig(
            service_type=ServiceType.PHENOMENOLOGY,
            port=8400
        )
        
        instance_id = self.service_manager.register_service(config)
        self.service_manager.start_service(instance_id)
        
        # Start monitoring
        self.service_manager.start_monitoring()
        
        # Wait a bit for monitoring to run
        time.sleep(0.5)
        
        # Check that service is being monitored
        instance = self.service_manager.services[instance_id]
        self.assertIsNotNone(instance.last_health_check)
        
        self.service_manager.stop_monitoring()

class TestServiceConfig(unittest.TestCase):
    """Test cases for ServiceConfig."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = ServiceConfig(service_type=ServiceType.MEANING_MAKING)
        
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.host, "localhost")
        self.assertEqual(config.workers, 1)
        self.assertEqual(config.memory_limit, 1024)
        self.assertEqual(config.cpu_limit, 1.0)
        self.assertTrue(config.auto_restart)
        self.assertEqual(config.health_check_interval, 30)
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = ServiceConfig(
            service_type=ServiceType.INTEGRATION,
            port=9000,
            memory_limit=2048,
            cpu_limit=2.0,
            auto_restart=False
        )
        
        self.assertEqual(config.port, 9000)
        self.assertEqual(config.memory_limit, 2048)
        self.assertEqual(config.cpu_limit, 2.0)
        self.assertFalse(config.auto_restart)

if __name__ == '__main__':
    unittest.main()