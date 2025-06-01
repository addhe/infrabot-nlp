"""
Networking Agent for GCP ADK Infrastructure Management.

This agent specializes in GCP networking operations including VPC networks,
subnets, firewall rules, load balancers, and connectivity management.
"""

from typing import Dict, Any, List, Optional
from ..base.base_agent import SpecializedGCPAgent
from ..tools.networking_tools import NetworkingTools


class NetworkingAgent(SpecializedGCPAgent):
    """
    Specialized agent for GCP networking infrastructure management.
    
    Handles VPC networks, subnets, firewall rules, load balancers,
    Cloud NAT, VPN connections, and network security policies.
    """
    
    def __init__(self, session_service, model: str = "gemini-1.5-pro"):
        """Initialize the Networking Agent with comprehensive networking capabilities."""
        super().__init__(
            name="networking_agent",
            model=model,
            session_service=session_service,
            description="GCP networking infrastructure specialist handling VPC networks, subnets, firewall rules, load balancers, and connectivity solutions.",
            instruction=self._get_networking_instructions(),
            tools=self._register_networking_tools()
        )
    
    def _get_networking_instructions(self) -> str:
        """Get comprehensive networking-specific instructions."""
        return """
You are a GCP Networking Infrastructure Specialist with deep expertise in cloud networking architectures, security, and connectivity solutions.

## CORE NETWORKING RESPONSIBILITIES:

### VPC Network Management:
- Design and implement VPC networks with proper CIDR planning
- Create and manage subnets across multiple regions and zones
- Configure network peering and shared VPC architectures
- Implement network segmentation and isolation strategies

### Firewall and Security:
- Design comprehensive firewall rule hierarchies
- Implement network security policies and IAM integration
- Configure Cloud Armor for DDoS protection and WAF rules
- Manage VPC firewall rules with priority optimization

### Load Balancing Solutions:
- Design and configure Application Load Balancers (Layer 7)
- Implement Network Load Balancers (Layer 4) for high performance
- Configure SSL certificates and HTTPS redirect policies
- Optimize backend services and health check configurations

### Connectivity and Hybrid Solutions:
- Configure Cloud VPN for secure site-to-site connectivity
- Implement Cloud Interconnect for dedicated connections
- Set up Cloud NAT for outbound internet access
- Design Cloud Router configurations for dynamic routing

### Network Monitoring and Optimization:
- Configure VPC Flow Logs for traffic analysis
- Implement network monitoring and alerting
- Optimize network performance and bandwidth usage
- Design disaster recovery and failover strategies

## NETWORKING BEST PRACTICES:

### CIDR Planning:
- Use RFC 1918 private address spaces efficiently
- Plan for future growth and avoid overlapping ranges
- Consider multi-region deployments and peering requirements
- Document IP allocation and subnet assignments

### Security First Design:
- Implement principle of least privilege for firewall rules
- Use service accounts and IAM for fine-grained access control
- Enable Private Google Access for secure API communication
- Configure network tags for organized security policies

### High Availability:
- Design multi-zone and multi-region architectures
- Implement redundant connectivity paths
- Configure health checks and automatic failover
- Plan for disaster recovery scenarios

### Performance Optimization:
- Choose appropriate load balancer types for workloads
- Optimize network placement and proximity rules
- Configure backend service timeout and retry policies
- Monitor and tune network latency and throughput

## SAFETY AND COMPLIANCE:

### Change Management:
- Validate firewall changes before implementation
- Test connectivity in non-production environments first
- Implement gradual rollout for critical network changes
- Maintain network documentation and change logs

### Security Validation:
- Review firewall rules for overly permissive access
- Validate SSL certificate configurations and expiration
- Check for unused or redundant network resources
- Ensure compliance with organizational security policies

### Cost Optimization:
- Monitor and optimize egress charges and data transfer costs
- Right-size load balancer configurations
- Clean up unused external IP addresses and NAT gateways
- Implement efficient routing policies

## ESCALATION TRIGGERS:
- Production firewall rule modifications affecting critical services
- Changes to shared VPC or network peering configurations
- SSL certificate updates for customer-facing applications
- Network connectivity issues affecting multiple services
- Security policy changes with broad organizational impact

Always consider network dependencies, security implications, and performance impact when making networking changes. Coordinate with security and operations teams for changes affecting production traffic.
"""
    
    def _register_networking_tools(self) -> List[Any]:
        """Register networking-specific tools."""
        networking_tools = NetworkingTools()
        
        return [
            # VPC and Subnet Management
            networking_tools.create_vpc_network,
            networking_tools.list_vpc_networks,
            networking_tools.delete_vpc_network,
            networking_tools.create_subnet,
            networking_tools.list_subnets,
            networking_tools.delete_subnet,
            
            # Firewall Management
            networking_tools.create_firewall_rule,
            networking_tools.list_firewall_rules,
            networking_tools.update_firewall_rule,
            networking_tools.delete_firewall_rule,
            
            # Load Balancer Management
            networking_tools.create_load_balancer,
            networking_tools.list_load_balancers,
            networking_tools.update_load_balancer,
            networking_tools.delete_load_balancer,
            
            # External IP Management
            networking_tools.reserve_external_ip,
            networking_tools.list_external_ips,
            networking_tools.release_external_ip,
            
            # Cloud NAT and Router
            networking_tools.create_cloud_nat,
            networking_tools.list_cloud_nats,
            networking_tools.delete_cloud_nat,
            networking_tools.create_cloud_router,
            networking_tools.list_cloud_routers,
            networking_tools.delete_cloud_router,
            
            # Network Security
            networking_tools.create_security_policy,
            networking_tools.list_security_policies,
            networking_tools.update_security_policy,
            networking_tools.delete_security_policy,
            
            # SSL Certificates
            networking_tools.create_ssl_certificate,
            networking_tools.list_ssl_certificates,
            networking_tools.delete_ssl_certificate,
            
            # Network Monitoring
            networking_tools.get_network_metrics,
            networking_tools.analyze_vpc_flow_logs,
            networking_tools.check_connectivity,
        ]
    
    def delegate_request(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle networking-specific requests with specialized logic.
        
        Args:
            request: The networking request to process
            context: Additional context including session state
            
        Returns:
            Response with networking analysis and recommendations
        """
        # Analyze request for networking patterns
        networking_keywords = {
            'vpc': ['vpc', 'network', 'virtual private cloud'],
            'subnet': ['subnet', 'subnetwork', 'cidr'],
            'firewall': ['firewall', 'security', 'ingress', 'egress'],
            'load_balancer': ['load balancer', 'lb', 'traffic', 'distribution'],
            'ssl': ['ssl', 'certificate', 'https', 'tls'],
            'nat': ['nat', 'outbound', 'internet access'],
            'vpn': ['vpn', 'connection', 'tunnel', 'site-to-site'],
            'peering': ['peering', 'interconnect', 'connectivity']
        }
        
        # Determine networking focus
        request_lower = request.lower()
        detected_components = []
        
        for component, keywords in networking_keywords.items():
            if any(keyword in request_lower for keyword in keywords):
                detected_components.append(component)
        
        # Add networking-specific context
        enhanced_context = {
            **context,
            'networking_components': detected_components,
            'requires_security_review': any(keyword in request_lower for keyword in ['firewall', 'security', 'ssl', 'certificate']),
            'affects_production_traffic': any(keyword in request_lower for keyword in ['production', 'prod', 'live', 'customer-facing']),
            'networking_scope': 'multi_region' if 'region' in request_lower or 'global' in request_lower else 'single_region'
        }
        
        # Check for high-risk operations
        high_risk_operations = [
            'delete vpc', 'remove network', 'delete firewall',
            'modify security policy', 'change ssl certificate',
            'update load balancer', 'remove connectivity'
        ]
        
        if any(operation in request_lower for operation in high_risk_operations):
            enhanced_context['requires_confirmation'] = True
            enhanced_context['risk_level'] = 'high'
        
        return {
            'agent': self.name,
            'specialization': 'networking',
            'context': enhanced_context,
            'recommendations': self._get_networking_recommendations(detected_components, context),
            'safety_checks': self._get_networking_safety_checks(request_lower, enhanced_context)
        }
    
    def _get_networking_recommendations(self, components: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate networking-specific recommendations."""
        recommendations = []
        
        if 'vpc' in components:
            recommendations.extend([
                "Plan CIDR ranges carefully to avoid conflicts with existing networks",
                "Consider enabling Private Google Access for secure API communication",
                "Design for multi-zone deployment for high availability"
            ])
        
        if 'firewall' in components:
            recommendations.extend([
                "Apply principle of least privilege for firewall rules",
                "Use descriptive names and tags for organization",
                "Test firewall changes in non-production environments first"
            ])
        
        if 'load_balancer' in components:
            recommendations.extend([
                "Configure appropriate health checks for backend services",
                "Consider SSL certificate management and renewal",
                "Plan for traffic distribution and backend scaling"
            ])
        
        if 'ssl' in components:
            recommendations.extend([
                "Monitor certificate expiration dates",
                "Use Google-managed certificates when possible",
                "Plan for certificate rotation and update procedures"
            ])
        
        # Add environment-specific recommendations
        if context.get('environment') == 'production':
            recommendations.extend([
                "Coordinate with operations team for production changes",
                "Implement gradual rollout for critical networking changes",
                "Ensure monitoring and alerting are in place"
            ])
        
        return recommendations
    
    def _get_networking_safety_checks(self, request: str, context: Dict[str, Any]) -> List[str]:
        """Generate networking-specific safety checks."""
        safety_checks = []
        
        # Firewall safety checks
        if 'firewall' in request:
            safety_checks.extend([
                "Verify firewall rules don't create overly permissive access",
                "Check for conflicts with existing security policies",
                "Validate source and destination ranges"
            ])
        
        # Load balancer safety checks
        if 'load balancer' in request or 'lb' in request:
            safety_checks.extend([
                "Ensure backend services are healthy and available",
                "Verify SSL certificate configuration if applicable",
                "Check for traffic distribution impact"
            ])
        
        # VPC safety checks
        if 'vpc' in request or 'network' in request:
            safety_checks.extend([
                "Verify CIDR ranges don't overlap with existing networks",
                "Check for dependencies on network resources",
                "Validate routing table configurations"
            ])
        
        # Production environment checks
        if context.get('affects_production_traffic'):
            safety_checks.extend([
                "Schedule change during maintenance window",
                "Prepare rollback plan for network changes",
                "Notify stakeholders of potential traffic impact"
            ])
        
        # High-risk operation checks
        if context.get('risk_level') == 'high':
            safety_checks.extend([
                "Obtain approval from network administrator",
                "Create backup of current configuration",
                "Test changes in staging environment first"
            ])
        
        return safety_checks