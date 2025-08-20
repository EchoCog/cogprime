"""
Cognitive Daemon - Main orchestration daemon for VM-Daemon-Sys

Provides the main entry point and coordination for the cognitive service ecosystem.
"""

import asyncio
import signal
import logging
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import json

from .service_manager import ServiceManager, ServiceConfig, ServiceType, ServiceStatus
from .load_balancer import LoadBalancer, LoadBalancingStrategy
from .health_monitor import HealthMonitor
from .orchestrator import CognitiveOrchestrator

logger = logging.getLogger(__name__)

class CognitiveDaemon:
    """Main daemon process for cognitive service orchestration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: Dict = {}
        self.service_manager: Optional[ServiceManager] = None
        self.load_balancer: Optional[LoadBalancer] = None
        self.health_monitor: Optional[HealthMonitor] = None
        self.orchestrator: Optional[CognitiveOrchestrator] = None
        self.running = False
        
        # Set up logging
        self._setup_logging()
        
        # Load configuration
        if config_path:
            self.load_config(config_path)
        else:
            self._load_default_config()
    
    def _setup_logging(self):
        """Configure logging for the daemon."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('cognitive_daemon.log')
            ]
        )
    
    def load_config(self, config_path: str):
        """Load configuration from file."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
            with open(config_file, 'r') as f:
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    self.config = yaml.safe_load(f)
                elif config_file.suffix.lower() == '.json':
                    self.config = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {config_file.suffix}")
            
            logger.info(f"Loaded configuration from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration."""
        self.config = {
            'daemon': {
                'port': 8080,
                'host': '0.0.0.0',
                'workers': 4,
                'log_level': 'INFO'
            },
            'services': {
                'relevance': {
                    'instances': 2,
                    'port_start': 8100,
                    'memory_limit': 512,
                    'cpu_limit': 0.5
                },
                'wisdom': {
                    'instances': 1,
                    'port_start': 8200,
                    'memory_limit': 1024,
                    'cpu_limit': 1.0
                },
                'rationality': {
                    'instances': 1,
                    'port_start': 8300,
                    'memory_limit': 512,
                    'cpu_limit': 0.5
                },
                'phenomenology': {
                    'instances': 1,
                    'port_start': 8400,
                    'memory_limit': 512,
                    'cpu_limit': 0.5
                },
                'meaning_making': {
                    'instances': 1,
                    'port_start': 8500,
                    'memory_limit': 512,
                    'cpu_limit': 0.5
                },
                'integration': {
                    'instances': 1,
                    'port_start': 8600,
                    'memory_limit': 1024,
                    'cpu_limit': 1.0
                },
                'silicon_sage': {
                    'instances': 1,
                    'port_start': 8700,
                    'memory_limit': 2048,
                    'cpu_limit': 2.0,
                    'dependencies': ['relevance', 'wisdom', 'rationality', 'phenomenology', 'meaning_making', 'integration']
                }
            },
            'load_balancer': {
                'strategy': 'round_robin',
                'health_check_interval': 30,
                'failure_threshold': 3
            },
            'monitoring': {
                'metrics_interval': 60,
                'alerts_enabled': True,
                'log_level': 'INFO'
            }
        }
        logger.info("Using default configuration")
    
    async def start(self):
        """Start the cognitive daemon."""
        if self.running:
            logger.warning("Daemon is already running")
            return
        
        try:
            logger.info("Starting Cognitive Daemon")
            
            # Initialize components
            await self._initialize_components()
            
            # Register signal handlers
            self._setup_signal_handlers()
            
            # Start all services
            await self._start_services()
            
            self.running = True
            logger.info("Cognitive Daemon started successfully")
            
            # Keep daemon running
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"Failed to start daemon: {e}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the cognitive daemon."""
        if not self.running:
            return
        
        logger.info("Stopping Cognitive Daemon")
        self.running = False
        
        try:
            # Stop all services
            if self.service_manager:
                await self._stop_all_services()
            
            # Stop components
            if self.health_monitor:
                self.health_monitor.stop()
            
            if self.service_manager:
                self.service_manager.stop_monitoring()
            
            logger.info("Cognitive Daemon stopped")
            
        except Exception as e:
            logger.error(f"Error stopping daemon: {e}")
    
    async def _initialize_components(self):
        """Initialize daemon components."""
        # Initialize service manager
        self.service_manager = ServiceManager()
        self.service_manager.start_monitoring()
        
        # Initialize load balancer
        strategy = LoadBalancingStrategy(self.config['load_balancer']['strategy'])
        self.load_balancer = LoadBalancer(
            strategy=strategy,
            service_manager=self.service_manager
        )
        
        # Initialize health monitor
        self.health_monitor = HealthMonitor(
            service_manager=self.service_manager,
            check_interval=self.config['monitoring']['metrics_interval']
        )
        self.health_monitor.start()
        
        # Initialize orchestrator
        self.orchestrator = CognitiveOrchestrator(
            service_manager=self.service_manager,
            load_balancer=self.load_balancer
        )
        
        # Register services from config
        self._register_services_from_config()
    
    def _register_services_from_config(self):
        """Register services based on configuration."""
        services_config = self.config.get('services', {})
        
        for service_name, service_config in services_config.items():
            try:
                service_type = ServiceType(service_name)
                instances = service_config.get('instances', 1)
                port_start = service_config.get('port_start', 8000)
                
                # Create multiple instances if specified
                for i in range(instances):
                    config = ServiceConfig(
                        service_type=service_type,
                        port=port_start + i,
                        memory_limit=service_config.get('memory_limit', 512),
                        cpu_limit=service_config.get('cpu_limit', 0.5),
                        dependencies=[ServiceType(dep) for dep in service_config.get('dependencies', [])]
                    )
                    
                    instance_id = self.service_manager.register_service(config)
                    logger.info(f"Registered {service_name} instance {i+1}: {instance_id}")
                    
            except ValueError as e:
                logger.error(f"Invalid service type '{service_name}': {e}")
            except Exception as e:
                logger.error(f"Failed to register service '{service_name}': {e}")
    
    async def _start_services(self):
        """Start all registered services in dependency order."""
        # Determine startup order based on dependencies
        startup_order = self._get_service_startup_order()
        
        for service_type in startup_order:
            instances = self.service_manager.get_services_by_type(service_type)
            
            for instance in instances:
                success = self.service_manager.start_service(instance.config.instance_id)
                if success:
                    logger.info(f"Started {service_type.value} service: {instance.config.instance_id}")
                else:
                    logger.error(f"Failed to start {service_type.value} service: {instance.config.instance_id}")
                
                # Brief delay between service starts
                await asyncio.sleep(2)
    
    async def _stop_all_services(self):
        """Stop all running services."""
        for instance_id in list(self.service_manager.services.keys()):
            self.service_manager.stop_service(instance_id)
    
    def _get_service_startup_order(self) -> List[ServiceType]:
        """Determine the order to start services based on dependencies."""
        # Simple topological sort for service dependencies
        order = []
        visited = set()
        
        def visit(service_type: ServiceType):
            if service_type in visited:
                return
            
            visited.add(service_type)
            
            # Get an instance to check dependencies
            instances = self.service_manager.get_services_by_type(service_type)
            if instances:
                for dep in instances[0].config.dependencies:
                    visit(dep)
            
            order.append(service_type)
        
        # Visit all service types
        for service_type in ServiceType:
            if self.service_manager.get_services_by_type(service_type):
                visit(service_type)
        
        return order
    
    async def _main_loop(self):
        """Main daemon loop."""
        while self.running:
            try:
                # Perform periodic maintenance
                await self._perform_maintenance()
                
                # Wait before next cycle
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)
    
    async def _perform_maintenance(self):
        """Perform periodic maintenance tasks."""
        # Check system health
        if self.health_monitor:
            health_status = self.health_monitor.get_system_health()
            if health_status['status'] != 'healthy':
                logger.warning(f"System health check failed: {health_status}")
        
        # Update load balancer
        if self.load_balancer:
            self.load_balancer.update_service_weights()
        
        # Log system status
        self._log_system_status()
    
    def _log_system_status(self):
        """Log current system status."""
        if not self.service_manager:
            return
        
        status_summary = {}
        for service_type in ServiceType:
            instances = self.service_manager.get_services_by_type(service_type)
            running_count = sum(1 for instance in instances 
                              if instance.status == ServiceStatus.RUNNING)
            total_count = len(instances)
            status_summary[service_type.value] = f"{running_count}/{total_count}"
        
        logger.info(f"Service status: {status_summary}")
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

def main():
    """Main entry point for the cognitive daemon."""
    parser = argparse.ArgumentParser(description="Cognitive Daemon for VM-Daemon-Sys")
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create and start daemon
    daemon = CognitiveDaemon(config_path=args.config)
    
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        logger.info("Received interrupt, shutting down")
    except Exception as e:
        logger.error(f"Daemon failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()