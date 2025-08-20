"""
Cognitive Orchestrator for VM-Daemon-Sys

High-level orchestration and coordination of cognitive services.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from .service_manager import ServiceManager, ServiceType, ServiceStatus
from .load_balancer import LoadBalancer
from .health_monitor import HealthMonitor, HealthStatus

logger = logging.getLogger(__name__)

@dataclass
class CognitiveRequest:
    """Request for cognitive processing."""
    request_id: str
    request_type: str
    content: str
    context: Dict[str, Any]
    priority: int = 1  # 1=low, 5=high
    complexity: float = 1.0  # Cognitive complexity estimate
    required_services: List[ServiceType] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.required_services is None:
            self.required_services = []

@dataclass
class CognitiveResponse:
    """Response from cognitive processing."""
    request_id: str
    status: str  # "success", "error", "partial"
    result: Dict[str, Any]
    processing_time: float
    services_used: List[str]
    confidence: float = 0.0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class CognitiveOrchestrator:
    """Orchestrates cognitive processing across multiple services."""
    
    def __init__(self, service_manager: ServiceManager, load_balancer: LoadBalancer):
        self.service_manager = service_manager
        self.load_balancer = load_balancer
        self.active_requests: Dict[str, CognitiveRequest] = {}
        self.request_queue: List[CognitiveRequest] = []
        self.processing_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_processing_time': 0.0
        }
    
    async def process_request(self, request: CognitiveRequest) -> CognitiveResponse:
        """Process a cognitive request through the appropriate services."""
        start_time = datetime.now()
        self.active_requests[request.request_id] = request
        self.processing_stats['total_requests'] += 1
        
        try:
            logger.info(f"Processing cognitive request {request.request_id} of type {request.request_type}")
            
            # Determine required services if not specified
            if not request.required_services:
                request.required_services = self._determine_required_services(request)
            
            # Plan processing pipeline
            pipeline = self._plan_processing_pipeline(request)
            
            # Execute pipeline
            result = await self._execute_pipeline(request, pipeline)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create response
            response = CognitiveResponse(
                request_id=request.request_id,
                status="success",
                result=result,
                processing_time=processing_time,
                services_used=pipeline,
                confidence=result.get('confidence', 0.8)
            )
            
            # Update stats
            self.processing_stats['successful_requests'] += 1
            self._update_average_processing_time(processing_time)
            
            logger.info(f"Successfully processed request {request.request_id} in {processing_time:.2f}s")
            return response
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error processing request {request.request_id}: {e}")
            
            # Update stats
            self.processing_stats['failed_requests'] += 1
            self._update_average_processing_time(processing_time)
            
            return CognitiveResponse(
                request_id=request.request_id,
                status="error",
                result={},
                processing_time=processing_time,
                services_used=[],
                errors=[str(e)]
            )
        
        finally:
            # Clean up
            self.active_requests.pop(request.request_id, None)
    
    async def process_silicon_sage_request(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a request through the SiliconSage orchestrator."""
        # Create cognitive request
        request = CognitiveRequest(
            request_id=f"sage_{datetime.now().timestamp()}",
            request_type="silicon_sage_advice",
            content=message,
            context=context,
            complexity=self._estimate_complexity(message, context),
            required_services=[ServiceType.SILICON_SAGE]
        )
        
        # Process through SiliconSage
        response = await self.process_request(request)
        
        if response.status == "success":
            return response.result
        else:
            return {
                "error": "Processing failed",
                "details": response.errors,
                "refined_message": message,
                "message_confidence": 0.0
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return self.processing_stats.copy()
    
    def get_active_requests(self) -> List[Dict[str, Any]]:
        """Get information about currently active requests."""
        return [
            {
                'request_id': req.request_id,
                'request_type': req.request_type,
                'priority': req.priority,
                'complexity': req.complexity,
                'timestamp': req.timestamp.isoformat(),
                'required_services': [s.value for s in req.required_services]
            }
            for req in self.active_requests.values()
        ]
    
    def _determine_required_services(self, request: CognitiveRequest) -> List[ServiceType]:
        """Determine which services are required for a request."""
        required_services = []
        
        # Basic mapping based on request type
        if request.request_type == "relevance_analysis":
            required_services = [ServiceType.RELEVANCE]
        elif request.request_type == "wisdom_evaluation":
            required_services = [ServiceType.WISDOM]
        elif request.request_type == "rational_analysis":
            required_services = [ServiceType.RATIONALITY]
        elif request.request_type == "phenomenological_processing":
            required_services = [ServiceType.PHENOMENOLOGY]
        elif request.request_type == "meaning_making":
            required_services = [ServiceType.MEANING_MAKING]
        elif request.request_type == "integration":
            required_services = [ServiceType.INTEGRATION]
        elif request.request_type == "silicon_sage_advice":
            required_services = [ServiceType.SILICON_SAGE]
        elif request.request_type == "comprehensive_analysis":
            # Use multiple services for comprehensive analysis
            required_services = [
                ServiceType.RELEVANCE,
                ServiceType.WISDOM,
                ServiceType.RATIONALITY,
                ServiceType.MEANING_MAKING,
                ServiceType.INTEGRATION
            ]
        else:
            # Default to SiliconSage for unknown request types
            required_services = [ServiceType.SILICON_SAGE]
        
        # Consider complexity for additional services
        if request.complexity > 0.7:
            if ServiceType.INTEGRATION not in required_services:
                required_services.append(ServiceType.INTEGRATION)
        
        return required_services
    
    def _plan_processing_pipeline(self, request: CognitiveRequest) -> List[str]:
        """Plan the processing pipeline for a request."""
        pipeline = []
        
        # For each required service, select the best instance
        for service_type in request.required_services:
            # Create request context for load balancer
            lb_context = {
                'complexity': request.complexity,
                'priority': request.priority,
                'request_type': request.request_type
            }
            
            instance_id = self.load_balancer.select_service_instance(service_type, lb_context)
            if instance_id:
                pipeline.append(instance_id)
            else:
                logger.warning(f"No available instance for service {service_type.value}")
        
        return pipeline
    
    async def _execute_pipeline(self, request: CognitiveRequest, pipeline: List[str]) -> Dict[str, Any]:
        """Execute the processing pipeline."""
        result = {}
        intermediate_results = {}
        
        for instance_id in pipeline:
            try:
                # Get service type for this instance
                instance = self.service_manager.services.get(instance_id)
                if not instance:
                    logger.error(f"Instance not found: {instance_id}")
                    continue
                
                service_type = instance.config.service_type
                
                # Record request start for load balancing
                self.load_balancer.record_request_start(instance_id)
                
                start_time = datetime.now()
                
                # Process with this service
                service_result = await self._process_with_service(
                    service_type, 
                    request.content, 
                    request.context,
                    intermediate_results
                )
                
                # Record request completion
                processing_time = (datetime.now() - start_time).total_seconds() * 1000  # ms
                self.load_balancer.record_request_end(instance_id, processing_time, True)
                
                # Store result
                intermediate_results[service_type.value] = service_result
                result.update(service_result)
                
                logger.debug(f"Processed with {service_type.value}: {instance_id}")
                
            except Exception as e:
                logger.error(f"Error processing with {instance_id}: {e}")
                
                # Record failed request
                processing_time = 5000  # Default for failed requests
                self.load_balancer.record_request_end(instance_id, processing_time, False)
                
                # Continue with other services
                continue
        
        return result
    
    async def _process_with_service(self, service_type: ServiceType, content: str, 
                                  context: Dict[str, Any], 
                                  intermediate_results: Dict[str, Any]) -> Dict[str, Any]:
        """Process content with a specific service."""
        # In a real implementation, this would make HTTP requests to the service
        # For simulation, we'll return appropriate mock responses
        
        if service_type == ServiceType.RELEVANCE:
            return {
                'relevance_scores': {'key_concept_1': 0.8, 'key_concept_2': 0.6},
                'salience_weights': {'attention': 0.7, 'working_memory': 0.5}
            }
        
        elif service_type == ServiceType.WISDOM:
            return {
                'wisdom_metrics': {
                    'inference': 0.75,
                    'insight': 0.65,
                    'intuition': 0.55,
                    'understanding': 0.80
                },
                'recommendations': ['Consider multiple perspectives', 'Balance analysis with intuition']
            }
        
        elif service_type == ServiceType.RATIONALITY:
            return {
                'rationality_metrics': {
                    'logical_coherence': 0.85,
                    'evidence_quality': 0.70,
                    'argument_strength': 0.75
                },
                'logical_analysis': 'The argument follows a coherent structure...'
            }
        
        elif service_type == ServiceType.PHENOMENOLOGY:
            return {
                'experiential_depth': 0.65,
                'participatory_knowing': 0.70,
                'meaning_resonance': 0.75
            }
        
        elif service_type == ServiceType.MEANING_MAKING:
            return {
                'refined_message': f"Enhanced: {content}",
                'message_confidence': 0.85,
                'meaning_depth': 0.80
            }
        
        elif service_type == ServiceType.INTEGRATION:
            return {
                'integration_level': 0.75,
                'synergistic_patterns': ['pattern_1', 'pattern_2'],
                'emergent_insights': ['insight_1', 'insight_2']
            }
        
        elif service_type == ServiceType.SILICON_SAGE:
            # SiliconSage provides comprehensive response
            return {
                'refined_message': f"Sage wisdom: {content}",
                'message_confidence': 0.85,
                'wisdom_metrics': {
                    'inference': 0.75,
                    'insight': 0.65,
                    'understanding': 0.80
                },
                'rationality_metrics': {
                    'logical_coherence': 0.85,
                    'evidence_quality': 0.70
                },
                'ecology_metrics': {
                    'integration_level': 0.75,
                    'optimization_depth': 0.70
                },
                'recommendations': [
                    'Consider multiple cognitive perspectives',
                    'Balance rational analysis with intuitive insights',
                    'Integrate findings across domains'
                ]
            }
        
        else:
            return {'error': f'Unknown service type: {service_type.value}'}
    
    def _estimate_complexity(self, message: str, context: Dict[str, Any]) -> float:
        """Estimate the cognitive complexity of a request."""
        complexity = 0.5  # Base complexity
        
        # Length factor
        message_length = len(message.split())
        if message_length > 100:
            complexity += 0.2
        elif message_length > 50:
            complexity += 0.1
        
        # Context complexity
        context_size = len(context)
        if context_size > 5:
            complexity += 0.2
        elif context_size > 2:
            complexity += 0.1
        
        # Content complexity indicators
        complex_terms = ['meaning', 'wisdom', 'consciousness', 'phenomenology', 'relevance']
        for term in complex_terms:
            if term in message.lower():
                complexity += 0.1
        
        return min(1.0, complexity)
    
    def _update_average_processing_time(self, processing_time: float):
        """Update the average processing time statistic."""
        total_requests = self.processing_stats['total_requests']
        current_avg = self.processing_stats['average_processing_time']
        
        # Calculate new average
        new_avg = ((current_avg * (total_requests - 1)) + processing_time) / total_requests
        self.processing_stats['average_processing_time'] = new_avg