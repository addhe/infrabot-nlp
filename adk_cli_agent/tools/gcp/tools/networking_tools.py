"""
Networking Tools for GCP ADK Infrastructure Management.

Provides comprehensive networking tools for VPC networks, subnets, firewall rules,
load balancers, and connectivity management.
"""

import json
import subprocess
from typing import Dict, Any, List, Optional, Union

try:
    from ...base.tool_context import ToolContext
except ImportError:
    # Fallback for development/testing
    class ToolContext:
        def __init__(self):
            pass
        def get_project_id(self):
            return None
        def log_operation(self, operation, details):
            pass


class NetworkingTools:
    """Tools for GCP networking operations."""
    
    def __init__(self):
        """Initialize networking tools."""
        self.context = ToolContext()
    
    def create_vpc_network(
        self,
        project_id: str,
        network_name: str,
        subnet_mode: str = "custom",
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a VPC network.
        
        Args:
            project_id: GCP project ID
            network_name: Name for the VPC network
            subnet_mode: Subnet creation mode (custom, auto, legacy)
            description: Optional description for the network
            
        Returns:
            Network creation result
        """
        try:
            cmd = [
                "gcloud", "compute", "networks", "create", network_name,
                "--project", project_id,
                "--subnet-mode", subnet_mode
            ]
            
            if description:
                cmd.extend(["--description", description])
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "network": json.loads(result.stdout) if result.stdout else {},
                "message": f"VPC network '{network_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create VPC network: {e.stderr}",
                "command": " ".join(cmd)
            }
    
    def list_vpc_networks(self, project_id: str) -> Dict[str, Any]:
        """
        List VPC networks in a project.
        
        Args:
            project_id: GCP project ID
            
        Returns:
            List of VPC networks
        """
        try:
            cmd = [
                "gcloud", "compute", "networks", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            networks = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "networks": networks,
                "count": len(networks)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list VPC networks: {e.stderr}"
            }
    
    def delete_vpc_network(self, project_id: str, network_name: str) -> Dict[str, Any]:
        """
        Delete a VPC network.
        
        Args:
            project_id: GCP project ID
            network_name: Name of the network to delete
            
        Returns:
            Deletion result
        """
        try:
            cmd = [
                "gcloud", "compute", "networks", "delete", network_name,
                "--project", project_id,
                "--quiet",
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"VPC network '{network_name}' deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete VPC network: {e.stderr}"
            }
    
    def create_subnet(
        self,
        project_id: str,
        subnet_name: str,
        network_name: str,
        region: str,
        range: str,
        secondary_ranges: Optional[List[Dict[str, str]]] = None,
        enable_private_ip_google_access: bool = False
    ) -> Dict[str, Any]:
        """
        Create a subnet in a VPC network.
        
        Args:
            project_id: GCP project ID
            subnet_name: Name for the subnet
            network_name: Parent VPC network name
            region: GCP region for the subnet
            range: CIDR range for the subnet
            secondary_ranges: Optional secondary IP ranges
            enable_private_ip_google_access: Enable Private Google Access
            
        Returns:
            Subnet creation result
        """
        try:
            cmd = [
                "gcloud", "compute", "networks", "subnets", "create", subnet_name,
                "--project", project_id,
                "--network", network_name,
                "--region", region,
                "--range", range
            ]
            
            if enable_private_ip_google_access:
                cmd.append("--enable-private-ip-google-access")
            
            if secondary_ranges:
                for secondary_range in secondary_ranges:
                    cmd.extend([
                        "--secondary-range",
                        f"{secondary_range['name']}={secondary_range['range']}"
                    ])
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "subnet": json.loads(result.stdout) if result.stdout else {},
                "message": f"Subnet '{subnet_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create subnet: {e.stderr}"
            }
    
    def list_subnets(self, project_id: str, region: Optional[str] = None) -> Dict[str, Any]:
        """
        List subnets in a project or region.
        
        Args:
            project_id: GCP project ID
            region: Optional region filter
            
        Returns:
            List of subnets
        """
        try:
            cmd = [
                "gcloud", "compute", "networks", "subnets", "list",
                "--project", project_id
            ]
            
            if region:
                cmd.extend(["--regions", region])
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            subnets = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "subnets": subnets,
                "count": len(subnets)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list subnets: {e.stderr}"
            }
    
    def delete_subnet(self, project_id: str, subnet_name: str, region: str) -> Dict[str, Any]:
        """
        Delete a subnet.
        
        Args:
            project_id: GCP project ID
            subnet_name: Name of the subnet to delete
            region: Region of the subnet
            
        Returns:
            Deletion result
        """
        try:
            cmd = [
                "gcloud", "compute", "networks", "subnets", "delete", subnet_name,
                "--project", project_id,
                "--region", region,
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Subnet '{subnet_name}' deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete subnet: {e.stderr}"
            }
    
    def create_firewall_rule(
        self,
        project_id: str,
        rule_name: str,
        direction: str,
        action: str,
        network: str,
        priority: int = 1000,
        source_ranges: Optional[List[str]] = None,
        target_tags: Optional[List[str]] = None,
        allowed: Optional[List[Dict[str, str]]] = None,
        denied: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a firewall rule.
        
        Args:
            project_id: GCP project ID
            rule_name: Name for the firewall rule
            direction: Traffic direction (INGRESS, EGRESS)
            action: Rule action (ALLOW, DENY)
            network: Target VPC network
            priority: Rule priority (0-65534)
            source_ranges: Source IP ranges
            target_tags: Target instance tags
            allowed: Allowed protocols and ports
            denied: Denied protocols and ports
            
        Returns:
            Firewall rule creation result
        """
        try:
            cmd = [
                "gcloud", "compute", "firewall-rules", "create", rule_name,
                "--project", project_id,
                "--direction", direction,
                "--action", action,
                "--network", network,
                "--priority", str(priority)
            ]
            
            if source_ranges:
                cmd.extend(["--source-ranges", ",".join(source_ranges)])
            
            if target_tags:
                cmd.extend(["--target-tags", ",".join(target_tags)])
            
            if allowed:
                for rule in allowed:
                    protocol = rule.get("protocol", "tcp")
                    ports = rule.get("ports", "")
                    if ports:
                        cmd.extend(["--allow", f"{protocol}:{ports}"])
                    else:
                        cmd.extend(["--allow", protocol])
            
            if denied:
                for rule in denied:
                    protocol = rule.get("protocol", "tcp")
                    ports = rule.get("ports", "")
                    if ports:
                        cmd.extend(["--deny", f"{protocol}:{ports}"])
                    else:
                        cmd.extend(["--deny", protocol])
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "rule": json.loads(result.stdout) if result.stdout else {},
                "message": f"Firewall rule '{rule_name}' created successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to create firewall rule: {e.stderr}"
            }
    
    def list_firewall_rules(self, project_id: str) -> Dict[str, Any]:
        """
        List firewall rules in a project.
        
        Args:
            project_id: GCP project ID
            
        Returns:
            List of firewall rules
        """
        try:
            cmd = [
                "gcloud", "compute", "firewall-rules", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            rules = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "rules": rules,
                "count": len(rules)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list firewall rules: {e.stderr}"
            }
    
    def update_firewall_rule(
        self,
        project_id: str,
        rule_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update a firewall rule.
        
        Args:
            project_id: GCP project ID
            rule_name: Name of the rule to update
            **kwargs: Fields to update
            
        Returns:
            Update result
        """
        try:
            cmd = [
                "gcloud", "compute", "firewall-rules", "update", rule_name,
                "--project", project_id
            ]
            
            # Add update parameters based on kwargs
            for key, value in kwargs.items():
                if key == "source_ranges" and value:
                    cmd.extend(["--source-ranges", ",".join(value)])
                elif key == "target_tags" and value:
                    cmd.extend(["--target-tags", ",".join(value)])
                elif key == "priority" and value:
                    cmd.extend(["--priority", str(value)])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Firewall rule '{rule_name}' updated successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to update firewall rule: {e.stderr}"
            }
    
    def delete_firewall_rule(self, project_id: str, rule_name: str) -> Dict[str, Any]:
        """
        Delete a firewall rule.
        
        Args:
            project_id: GCP project ID
            rule_name: Name of the rule to delete
            
        Returns:
            Deletion result
        """
        try:
            cmd = [
                "gcloud", "compute", "firewall-rules", "delete", rule_name,
                "--project", project_id,
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"Firewall rule '{rule_name}' deleted successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to delete firewall rule: {e.stderr}"
            }
    
    # Load Balancer Management (placeholder methods)
    def create_load_balancer(self, **kwargs) -> Dict[str, Any]:
        """Create a load balancer (placeholder)."""
        return {"success": False, "error": "Load balancer creation not yet implemented"}
    
    def list_load_balancers(self, project_id: str) -> Dict[str, Any]:
        """List load balancers (placeholder)."""
        return {"success": False, "error": "Load balancer listing not yet implemented"}
    
    def update_load_balancer(self, **kwargs) -> Dict[str, Any]:
        """Update a load balancer (placeholder)."""
        return {"success": False, "error": "Load balancer update not yet implemented"}
    
    def delete_load_balancer(self, **kwargs) -> Dict[str, Any]:
        """Delete a load balancer (placeholder)."""
        return {"success": False, "error": "Load balancer deletion not yet implemented"}
    
    # External IP Management
    def reserve_external_ip(
        self,
        project_id: str,
        address_name: str,
        region: Optional[str] = None,
        global_scope: bool = False
    ) -> Dict[str, Any]:
        """
        Reserve an external IP address.
        
        Args:
            project_id: GCP project ID
            address_name: Name for the IP address
            region: Region for regional IP (required if not global)
            global_scope: Whether to create a global IP address
            
        Returns:
            IP reservation result
        """
        try:
            cmd = [
                "gcloud", "compute", "addresses", "create", address_name,
                "--project", project_id
            ]
            
            if global_scope:
                cmd.append("--global")
            elif region:
                cmd.extend(["--region", region])
            else:
                return {
                    "success": False,
                    "error": "Either region or global_scope must be specified"
                }
            
            cmd.append("--format=json")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "address": json.loads(result.stdout) if result.stdout else {},
                "message": f"External IP '{address_name}' reserved successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to reserve external IP: {e.stderr}"
            }
    
    def list_external_ips(self, project_id: str) -> Dict[str, Any]:
        """
        List external IP addresses.
        
        Args:
            project_id: GCP project ID
            
        Returns:
            List of external IP addresses
        """
        try:
            cmd = [
                "gcloud", "compute", "addresses", "list",
                "--project", project_id,
                "--format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            addresses = json.loads(result.stdout) if result.stdout else []
            
            return {
                "success": True,
                "addresses": addresses,
                "count": len(addresses)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to list external IPs: {e.stderr}"
            }
    
    def release_external_ip(
        self,
        project_id: str,
        address_name: str,
        region: Optional[str] = None,
        global_scope: bool = False
    ) -> Dict[str, Any]:
        """
        Release an external IP address.
        
        Args:
            project_id: GCP project ID
            address_name: Name of the IP address to release
            region: Region for regional IP
            global_scope: Whether it's a global IP address
            
        Returns:
            Release result
        """
        try:
            cmd = [
                "gcloud", "compute", "addresses", "delete", address_name,
                "--project", project_id,
                "--quiet"
            ]
            
            if global_scope:
                cmd.append("--global")
            elif region:
                cmd.extend(["--region", region])
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            return {
                "success": True,
                "message": f"External IP '{address_name}' released successfully"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Failed to release external IP: {e.stderr}"
            }
    
    # Placeholder methods for additional networking features
    def create_cloud_nat(self, **kwargs) -> Dict[str, Any]:
        """Create Cloud NAT (placeholder)."""
        return {"success": False, "error": "Cloud NAT creation not yet implemented"}
    
    def list_cloud_nats(self, project_id: str) -> Dict[str, Any]:
        """List Cloud NATs (placeholder)."""
        return {"success": False, "error": "Cloud NAT listing not yet implemented"}
    
    def delete_cloud_nat(self, **kwargs) -> Dict[str, Any]:
        """Delete Cloud NAT (placeholder)."""
        return {"success": False, "error": "Cloud NAT deletion not yet implemented"}
    
    def create_cloud_router(self, **kwargs) -> Dict[str, Any]:
        """Create Cloud Router (placeholder)."""
        return {"success": False, "error": "Cloud Router creation not yet implemented"}
    
    def list_cloud_routers(self, project_id: str) -> Dict[str, Any]:
        """List Cloud Routers (placeholder)."""
        return {"success": False, "error": "Cloud Router listing not yet implemented"}
    
    def delete_cloud_router(self, **kwargs) -> Dict[str, Any]:
        """Delete Cloud Router (placeholder)."""
        return {"success": False, "error": "Cloud Router deletion not yet implemented"}
    
    def create_security_policy(self, **kwargs) -> Dict[str, Any]:
        """Create security policy (placeholder)."""
        return {"success": False, "error": "Security policy creation not yet implemented"}
    
    def list_security_policies(self, project_id: str) -> Dict[str, Any]:
        """List security policies (placeholder)."""
        return {"success": False, "error": "Security policy listing not yet implemented"}
    
    def update_security_policy(self, **kwargs) -> Dict[str, Any]:
        """Update security policy (placeholder)."""
        return {"success": False, "error": "Security policy update not yet implemented"}
    
    def delete_security_policy(self, **kwargs) -> Dict[str, Any]:
        """Delete security policy (placeholder)."""
        return {"success": False, "error": "Security policy deletion not yet implemented"}
    
    def create_ssl_certificate(self, **kwargs) -> Dict[str, Any]:
        """Create SSL certificate (placeholder)."""
        return {"success": False, "error": "SSL certificate creation not yet implemented"}
    
    def list_ssl_certificates(self, project_id: str) -> Dict[str, Any]:
        """List SSL certificates (placeholder)."""
        return {"success": False, "error": "SSL certificate listing not yet implemented"}
    
    def delete_ssl_certificate(self, **kwargs) -> Dict[str, Any]:
        """Delete SSL certificate (placeholder)."""
        return {"success": False, "error": "SSL certificate deletion not yet implemented"}
    
    def get_network_metrics(self, **kwargs) -> Dict[str, Any]:
        """Get network metrics (placeholder)."""
        return {"success": False, "error": "Network metrics not yet implemented"}
    
    def analyze_vpc_flow_logs(self, **kwargs) -> Dict[str, Any]:
        """Analyze VPC flow logs (placeholder)."""
        return {"success": False, "error": "VPC flow log analysis not yet implemented"}
    
    def check_connectivity(self, **kwargs) -> Dict[str, Any]:
        """Check network connectivity (placeholder)."""
        return {"success": False, "error": "Connectivity check not yet implemented"}
