"""
Monitoring Agent for GCP ADK Implementation

Specialized agent for monitoring, logging, alerting, and observability management.
Handles Cloud Monitoring, Cloud Logging, Error Reporting, and alerting policies.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from ..base.base_agent import SpecializedGCPAgent

logger = logging.getLogger(__name__)


class MonitoringAgent(SpecializedGCPAgent):
    """
    Specialized agent for GCP monitoring and observability management.
    
    Capabilities:
    - Cloud Monitoring metrics and dashboards
    - Cloud Logging configuration and analysis
    - Alerting policies and notification channels
    - Error Reporting and application monitoring
    - APM and distributed tracing
    - SLI/SLO management and reporting
    """
    
    def __init__(self, session_service=None):
        """Initialize the monitoring agent."""
        super().__init__(
            name="monitoring_agent",
            specialization="observability_monitoring",
            session_service=session_service
        )
    
    def get_specialized_instructions(self) -> str:
        """Get specialized instructions for monitoring operations."""
        return """
        You are a specialized monitoring and observability agent with expertise in:

        MONITORING CAPABILITIES:
        - Cloud Monitoring metrics, alerts, and dashboards
        - Custom metrics and application monitoring
        - Infrastructure monitoring and resource utilization
        - Performance monitoring and optimization
        - Service Level Indicators (SLIs) and Service Level Objectives (SLOs)

        LOGGING CAPABILITIES:
        - Cloud Logging configuration and management
        - Log-based metrics and alerting
        - Log analysis and troubleshooting
        - Audit logging and compliance requirements
        - Structured logging best practices

        ALERTING CAPABILITIES:
        - Alerting policies and notification channels
        - Multi-condition alerts and escalation policies
        - Alert fatigue reduction and optimization
        - Incident response and automation
        - Integration with external systems (PagerDuty, Slack, etc.)

        ERROR REPORTING:
        - Application error tracking and analysis
        - Error grouping and prioritization
        - Integration with development workflows
        - Performance impact analysis

        APM AND TRACING:
        - Application Performance Monitoring setup
        - Distributed tracing configuration
        - Latency analysis and optimization
        - Dependency mapping and service mesh monitoring

        BEST PRACTICES:
        - Implement comprehensive monitoring strategies
        - Use appropriate alerting thresholds to avoid noise
        - Create meaningful dashboards for different stakeholders
        - Establish clear SLIs/SLOs for critical services
        - Implement proper log retention and archival policies
        - Use monitoring data for capacity planning
        - Implement effective incident response procedures

        SAFETY CONSIDERATIONS:
        - Monitor for security anomalies and threats
        - Implement alerting for compliance violations
        - Protect sensitive data in logs and metrics
        - Ensure monitoring doesn't impact application performance
        - Implement proper access controls for monitoring data
        """
    
    def can_handle_request(self, request: str) -> Dict[str, Any]:
        """
        Determine if this agent can handle the monitoring request.
        
        Args:
            request: The user request to analyze
            
        Returns:
            Assessment of whether this agent can handle the request
        """
        monitoring_keywords = [
            # Monitoring terms
            'monitor', 'monitoring', 'metrics', 'dashboard', 'observability',
            'telemetry', 'alerting', 'alerts', 'notification', 'slo', 'sli',
            
            # Logging terms
            'logging', 'logs', 'log analysis', 'audit logs', 'log retention',
            'log aggregation', 'log parsing', 'log-based metrics',
            
            # Error tracking
            'error reporting', 'error tracking', 'exception monitoring',
            'crash reporting', 'error analysis', 'error grouping',
            
            # APM terms
            'apm', 'application monitoring', 'performance monitoring',
            'tracing', 'distributed tracing', 'latency', 'performance',
            
            # Cloud services
            'cloud monitoring', 'cloud logging', 'stackdriver', 'operations suite',
            'error reporting', 'cloud trace', 'cloud profiler',
            
            # Infrastructure monitoring
            'system metrics', 'resource monitoring', 'cpu monitoring',
            'memory monitoring', 'disk monitoring', 'network monitoring',
            
            # Alerting
            'alert policy', 'notification channel', 'escalation', 'incident',
            'pager', 'on-call', 'alert fatigue', 'alert optimization'
        ]
        
        request_lower = request.lower()
        matching_keywords = [kw for kw in monitoring_keywords if kw in request_lower]
        
        # Check for monitoring-specific components
        monitoring_components = [
            'metric', 'dashboard', 'alert', 'log', 'trace', 'error',
            'notification', 'uptime check', 'slo', 'sli'
        ]
        
        component_matches = [comp for comp in monitoring_components if comp in request_lower]
        
        # Calculate confidence based on keyword matches
        confidence = min(0.9, len(matching_keywords) * 0.15 + len(component_matches) * 0.1)
        
        if confidence >= 0.3:
            return {
                "can_handle": True,
                "confidence": confidence,
                "reasoning": f"Request contains monitoring/observability keywords: {matching_keywords[:3]}",
                "matching_components": component_matches[:3]
            }
        
        return {
            "can_handle": False,
            "confidence": confidence,
            "reasoning": "Request does not contain sufficient monitoring or observability keywords"
        }
    
    def delegate_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate monitoring request to appropriate specialized handling.
        
        Args:
            request: The user request
            context: Additional context for the request
            
        Returns:
            Delegation decision and enhanced context
        """
        # Analyze request for monitoring components
        request_lower = request.lower()
        
        # Determine monitoring operation type
        operation_type = "general"
        if any(word in request_lower for word in ['create', 'setup', 'configure', 'install']):
            operation_type = "setup"
        elif any(word in request_lower for word in ['analyze', 'investigate', 'troubleshoot', 'debug']):
            operation_type = "analysis"
        elif any(word in request_lower for word in ['optimize', 'improve', 'tune', 'enhance']):
            operation_type = "optimization"
        elif any(word in request_lower for word in ['delete', 'remove', 'disable', 'cleanup']):
            operation_type = "cleanup"
        
        # Determine monitoring scope
        scope = "application"
        if any(word in request_lower for word in ['infrastructure', 'system', 'server', 'vm', 'instance']):
            scope = "infrastructure"
        elif any(word in request_lower for word in ['network', 'connectivity', 'bandwidth']):
            scope = "network"
        elif any(word in request_lower for word in ['security', 'compliance', 'audit']):
            scope = "security"
        elif any(word in request_lower for word in ['cost', 'billing', 'usage']):
            scope = "cost"
        
        # Risk assessment for monitoring operations
        risk_level = "low"
        risk_factors = []
        
        # Check for high-impact operations
        if any(word in request_lower for word in ['delete', 'remove', 'disable']):
            risk_level = "medium"
            risk_factors.append("Deletion/removal operations")
        
        if any(word in request_lower for word in ['production', 'prod', 'live']):
            if risk_level == "medium":
                risk_level = "high"
            elif risk_level == "low":
                risk_level = "medium"
            risk_factors.append("Production environment")
        
        if any(word in request_lower for word in ['all', 'entire', 'complete', 'full']):
            risk_level = "medium"
            risk_factors.append("Broad scope operation")
        
        # Monitoring-specific recommendations
        recommendations = []
        
        if operation_type == "setup":
            recommendations.extend([
                "Start with basic monitoring before adding complex metrics",
                "Implement alerting thresholds based on historical data",
                "Consider alert fatigue when setting up notifications",
                "Test alerting channels before deploying to production"
            ])
        
        if operation_type == "analysis":
            recommendations.extend([
                "Use correlation analysis to identify root causes",
                "Check for patterns across multiple time windows",
                "Consider external factors that might affect metrics",
                "Document findings for future reference"
            ])
        
        if scope == "security":
            recommendations.extend([
                "Implement monitoring for security anomalies",
                "Set up alerts for compliance violations",
                "Monitor access patterns and privilege escalation",
                "Ensure monitoring data is properly secured"
            ])
        
        if context.get('session_service'):
            context['session_service'].log_delegation({
                'agent': 'monitoring_agent',
                'operation_type': operation_type,
                'scope': scope,
                'risk_level': risk_level,
                'risk_factors': risk_factors
            })
        
        return {
            "should_handle": True,
            "agent": "monitoring_agent",
            "enhanced_context": {
                **context,
                "operation_type": operation_type,
                "monitoring_scope": scope,
                "risk_assessment": {
                    "level": risk_level,
                    "factors": risk_factors
                },
                "recommendations": recommendations,
                "monitoring_best_practices": [
                    "Implement comprehensive observability strategy",
                    "Use monitoring data for proactive issue resolution",
                    "Maintain appropriate alert signal-to-noise ratio",
                    "Regularly review and optimize monitoring configurations"
                ]
            }
        }
    
    def perform_safety_check(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform safety checks for monitoring operations.
        
        Args:
            request: The user request
            context: Enhanced context from delegation
            
        Returns:
            Safety check results and recommendations
        """
        safety_issues = []
        warnings = []
        requires_confirmation = False
        
        request_lower = request.lower()
        risk_level = context.get('risk_assessment', {}).get('level', 'low')
        
        # Check for high-risk monitoring operations
        if any(word in request_lower for word in ['delete', 'remove', 'disable']):
            if any(word in request_lower for word in ['alert', 'monitoring', 'dashboard']):
                safety_issues.append("Deleting monitoring components may reduce observability")
                requires_confirmation = True
        
        # Production environment checks
        if any(word in request_lower for word in ['production', 'prod', 'live']):
            warnings.append("Operating on production monitoring - ensure minimal impact")
            if any(word in request_lower for word in ['test', 'experiment']):
                safety_issues.append("Testing in production monitoring can affect alerting")
                requires_confirmation = True
        
        # Alert configuration safety
        if any(word in request_lower for word in ['alert', 'notification']):
            if any(word in request_lower for word in ['all', 'everyone', 'broadcast']):
                warnings.append("Broad alerting can cause alert fatigue and missed critical issues")
            
            if any(word in request_lower for word in ['aggressive', 'sensitive', 'low threshold']):
                warnings.append("Overly sensitive alerts may cause noise and alert fatigue")
        
        # Data retention and storage safety
        if any(word in request_lower for word in ['retention', 'archive', 'delete logs']):
            if any(word in request_lower for word in ['audit', 'compliance', 'regulatory']):
                safety_issues.append("Modifying log retention may impact compliance requirements")
                requires_confirmation = True
        
        # Cost implications
        if any(word in request_lower for word in ['all metrics', 'detailed monitoring', 'high frequency']):
            warnings.append("Extensive monitoring can increase costs significantly")
        
        # Security considerations
        if any(word in request_lower for word in ['external', 'public', 'internet']):
            if any(word in request_lower for word in ['webhook', 'notification', 'endpoint']):
                safety_issues.append("External monitoring endpoints may expose sensitive information")
                requires_confirmation = True
        
        return {
            "safe": len(safety_issues) == 0,
            "risk_level": risk_level,
            "safety_issues": safety_issues,
            "warnings": warnings,
            "requires_confirmation": requires_confirmation,
            "recommendations": [
                "Test monitoring configurations in non-production first",
                "Implement gradual rollout for monitoring changes",
                "Monitor the monitoring - track alert effectiveness",
                "Regular review and cleanup of unused monitoring resources",
                "Ensure monitoring doesn't become a performance bottleneck"
            ]
        }