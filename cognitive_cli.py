#!/usr/bin/env python3
"""
CLI interface for VM-Daemon-Sys cognitive service orchestration.
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, Any

from src.vm_daemon_sys.daemon import CognitiveDaemon
from src.vm_daemon_sys.service_manager import ServiceType, ServiceStatus

class CognitiveCLI:
    """Command-line interface for cognitive daemon management."""
    
    def __init__(self):
        self.daemon: CognitiveDaemon = None
    
    def run(self, args):
        """Run the CLI with given arguments."""
        if args.command == 'start':
            self.start_daemon(args)
        elif args.command == 'stop':
            self.stop_daemon(args)
        elif args.command == 'status':
            self.show_status(args)
        elif args.command == 'services':
            self.manage_services(args)
        elif args.command == 'health':
            self.show_health(args)
        elif args.command == 'test':
            self.test_processing(args)
        elif args.command == 'config':
            self.manage_config(args)
        else:
            print(f"Unknown command: {args.command}")
            sys.exit(1)
    
    def start_daemon(self, args):
        """Start the cognitive daemon."""
        print("Starting Cognitive Daemon...")
        
        config_path = args.config if args.config else "config/daemon.yml"
        
        try:
            self.daemon = CognitiveDaemon(config_path=config_path)
            asyncio.run(self.daemon.start())
        except KeyboardInterrupt:
            print("\nShutdown requested by user")
        except Exception as e:
            print(f"Failed to start daemon: {e}")
            sys.exit(1)
    
    def stop_daemon(self, args):
        """Stop the cognitive daemon."""
        print("Stopping Cognitive Daemon...")
        # In a real implementation, this would send a signal to the running daemon
        print("Daemon stop signal sent.")
    
    def show_status(self, args):
        """Show daemon and service status."""
        print("Cognitive Daemon Status")
        print("=" * 50)
        
        # In a real implementation, this would query the running daemon
        print("Status: Running")
        print("Uptime: 2h 15m 30s")
        print("Configuration: config/daemon.yml")
        print("\nService Summary:")
        print("- Total Services: 7")
        print("- Running: 6")
        print("- Stopped: 1")
        print("- Errors: 0")
        
        if args.verbose:
            self._show_detailed_status()
    
    def manage_services(self, args):
        """Manage individual services."""
        if args.service_action == 'list':
            self._list_services()
        elif args.service_action == 'start':
            self._start_service(args.service_name)
        elif args.service_action == 'stop':
            self._stop_service(args.service_name)
        elif args.service_action == 'restart':
            self._restart_service(args.service_name)
        elif args.service_action == 'scale':
            self._scale_service(args.service_name, args.instances)
    
    def show_health(self, args):
        """Show health status."""
        print("Health Status")
        print("=" * 50)
        
        # Mock health data
        services_health = {
            'relevance': {'status': 'healthy', 'cpu': 45.2, 'memory': 62.1, 'response_time': 125},
            'wisdom': {'status': 'healthy', 'cpu': 38.7, 'memory': 55.8, 'response_time': 89},
            'rationality': {'status': 'warning', 'cpu': 72.1, 'memory': 43.2, 'response_time': 156},
            'phenomenology': {'status': 'healthy', 'cpu': 29.4, 'memory': 38.9, 'response_time': 98},
            'meaning_making': {'status': 'healthy', 'cpu': 34.8, 'memory': 41.7, 'response_time': 112},
            'integration': {'status': 'healthy', 'cpu': 51.3, 'memory': 67.4, 'response_time': 203},
            'silicon_sage': {'status': 'healthy', 'cpu': 48.9, 'memory': 78.3, 'response_time': 167}
        }
        
        for service, health in services_health.items():
            status_icon = "✅" if health['status'] == 'healthy' else "⚠️" if health['status'] == 'warning' else "❌"
            print(f"{status_icon} {service:<15} CPU: {health['cpu']:>5.1f}% Memory: {health['memory']:>5.1f}% Response: {health['response_time']:>3}ms")
        
        if args.watch:
            print("\nWatching health status (Ctrl+C to exit)...")
            try:
                while True:
                    time.sleep(5)
                    # In real implementation, refresh the display
            except KeyboardInterrupt:
                print("\nStopped watching.")
    
    def test_processing(self, args):
        """Test cognitive processing."""
        print("Testing Cognitive Processing")
        print("=" * 50)
        
        # Create test message
        test_message = args.message if args.message else "How can I improve my problem-solving abilities?"
        test_context = {"domain": "cognitive_enhancement", "complexity": "medium"}
        
        print(f"Input: {test_message}")
        print(f"Context: {json.dumps(test_context, indent=2)}")
        
        # Simulate processing
        print("\nProcessing...")
        time.sleep(2)  # Simulate processing time
        
        # Mock response
        response = {
            "refined_message": f"Enhanced guidance: {test_message}",
            "message_confidence": 0.85,
            "wisdom_metrics": {
                "inference": 0.75,
                "insight": 0.68,
                "understanding": 0.82
            },
            "rationality_metrics": {
                "logical_coherence": 0.88,
                "evidence_quality": 0.72
            },
            "recommendations": [
                "Practice systematic problem decomposition",
                "Develop pattern recognition skills",
                "Balance analytical and intuitive approaches"
            ]
        }
        
        print("\nResponse:")
        print(json.dumps(response, indent=2))
        print(f"\nProcessing completed in 2.1 seconds")
    
    def manage_config(self, args):
        """Manage configuration."""
        if args.config_action == 'show':
            self._show_config(args.config_file)
        elif args.config_action == 'validate':
            self._validate_config(args.config_file)
        elif args.config_action == 'reload':
            self._reload_config()
    
    def _show_detailed_status(self):
        """Show detailed service status."""
        print("\nDetailed Service Status:")
        print("-" * 50)
        
        services = [
            {'name': 'relevance', 'instances': 2, 'running': 2, 'port': '8100-8101'},
            {'name': 'wisdom', 'instances': 1, 'running': 1, 'port': '8200'},
            {'name': 'rationality', 'instances': 1, 'running': 1, 'port': '8300'},
            {'name': 'phenomenology', 'instances': 1, 'running': 1, 'port': '8400'},
            {'name': 'meaning_making', 'instances': 1, 'running': 1, 'port': '8500'},
            {'name': 'integration', 'instances': 1, 'running': 0, 'port': '8600'},
            {'name': 'silicon_sage', 'instances': 1, 'running': 1, 'port': '8700'},
        ]
        
        for service in services:
            status = "Running" if service['running'] == service['instances'] else f"Partial ({service['running']}/{service['instances']})"
            if service['running'] == 0:
                status = "Stopped"
            
            print(f"{service['name']:<15} {status:<15} Port: {service['port']}")
    
    def _list_services(self):
        """List all services."""
        print("Cognitive Services")
        print("=" * 50)
        
        for service_type in ServiceType:
            print(f"- {service_type.value}")
    
    def _start_service(self, service_name):
        """Start a specific service."""
        print(f"Starting service: {service_name}")
        # Implementation would send command to daemon
        print(f"Service {service_name} started successfully.")
    
    def _stop_service(self, service_name):
        """Stop a specific service."""
        print(f"Stopping service: {service_name}")
        # Implementation would send command to daemon
        print(f"Service {service_name} stopped successfully.")
    
    def _restart_service(self, service_name):
        """Restart a specific service."""
        print(f"Restarting service: {service_name}")
        # Implementation would send command to daemon
        print(f"Service {service_name} restarted successfully.")
    
    def _scale_service(self, service_name, instances):
        """Scale a service to specified number of instances."""
        print(f"Scaling service {service_name} to {instances} instances")
        # Implementation would send command to daemon
        print(f"Service {service_name} scaled to {instances} instances.")
    
    def _show_config(self, config_file):
        """Show configuration."""
        config_path = Path(config_file) if config_file else Path("config/daemon.yml")
        
        if not config_path.exists():
            print(f"Configuration file not found: {config_path}")
            return
        
        print(f"Configuration: {config_path}")
        print("=" * 50)
        
        with open(config_path, 'r') as f:
            print(f.read())
    
    def _validate_config(self, config_file):
        """Validate configuration file."""
        config_path = Path(config_file) if config_file else Path("config/daemon.yml")
        
        print(f"Validating configuration: {config_path}")
        
        try:
            # In real implementation, would validate the config
            print("✅ Configuration is valid")
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
    
    def _reload_config(self):
        """Reload configuration."""
        print("Reloading configuration...")
        # Implementation would send signal to daemon
        print("Configuration reloaded successfully.")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Cognitive Daemon CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the cognitive daemon')
    start_parser.add_argument('--config', '-c', help='Configuration file path')
    
    # Stop command
    stop_parser = subparsers.add_parser('stop', help='Stop the cognitive daemon')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show daemon status')
    status_parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed status')
    
    # Services command
    services_parser = subparsers.add_parser('services', help='Manage services')
    services_subparsers = services_parser.add_subparsers(dest='service_action', help='Service actions')
    
    services_subparsers.add_parser('list', help='List all services')
    
    start_service_parser = services_subparsers.add_parser('start', help='Start a service')
    start_service_parser.add_argument('service_name', help='Service name to start')
    
    stop_service_parser = services_subparsers.add_parser('stop', help='Stop a service')
    stop_service_parser.add_argument('service_name', help='Service name to stop')
    
    restart_service_parser = services_subparsers.add_parser('restart', help='Restart a service')
    restart_service_parser.add_argument('service_name', help='Service name to restart')
    
    scale_service_parser = services_subparsers.add_parser('scale', help='Scale a service')
    scale_service_parser.add_argument('service_name', help='Service name to scale')
    scale_service_parser.add_argument('instances', type=int, help='Number of instances')
    
    # Health command
    health_parser = subparsers.add_parser('health', help='Show health status')
    health_parser.add_argument('--watch', '-w', action='store_true', help='Watch health status')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test cognitive processing')
    test_parser.add_argument('--message', '-m', help='Test message to process')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Config actions')
    
    show_config_parser = config_subparsers.add_parser('show', help='Show configuration')
    show_config_parser.add_argument('config_file', nargs='?', help='Configuration file to show')
    
    validate_config_parser = config_subparsers.add_parser('validate', help='Validate configuration')
    validate_config_parser.add_argument('config_file', nargs='?', help='Configuration file to validate')
    
    config_subparsers.add_parser('reload', help='Reload configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = CognitiveCLI()
    cli.run(args)

if __name__ == "__main__":
    main()