"""
GCP Subnet Management Module

This module provides comprehensive subnet management functionality including
subnet creation, listing, updating, and deletion within VPC networks.
"""

import logging
from typing import List, Optional, Dict, Any
from google.cloud import compute

from ..base import (
    GCPSubnet,
    GCPClientManager,
    get_client_manager,
    GCPToolsError,
    GCPResourceNotFoundError,
    GCPValidationError,
    GCPOperationError,
    validate_project_id,
    validate_subnet_name,
    validate_cidr_range,
    validate_region,
    format_resource_name,
    normalize_resource_name
)

# Create alias for backward compatibility
GCPResourceError = GCPToolsError
GCPError = GCPToolsError

logger = logging.getLogger(__name__)


class SubnetManager:
    """
    GCP Subnet management with comprehensive CRUD operations.
    
    This class provides methods for creating, listing, updating, and deleting
    subnets within VPC networks with proper error handling and validation.
    """
    
    def __init__(self, client_manager: Optional[GCPClientManager] = None):
        """
        Initialize subnet manager.
        
        Args:
            client_manager: GCP client manager instance
        """
        self.client_manager = client_manager or get_client_manager()
    
    def list_subnets(
        self,
        project_id: Optional[str] = None,
        region: Optional[str] = None,
        vpc_name: Optional[str] = None
    ) -> List[GCPSubnet]:
        """
        List subnets in a project with optional filtering.
        
        Args:
            project_id: GCP project ID (uses default if not provided)
            region: Region to filter by (optional)
            vpc_name: VPC network name to filter by (optional)
            
        Returns:
            List of GCPSubnet instances
            
        Raises:
            GCPError: If listing fails
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        if region:
            validate_region(region)
        
        try:
            client = self.client_manager.get_subnet_client()
            
            subnets = []
            
            if region:
                # List subnets in specific region
                request = compute.ListSubnetworksRequest(
                    project=project_id,
                    region=region
                )
                subnet_list = client.list(request=request)
                
                for subnet in subnet_list:
                    if not vpc_name or subnet.network.endswith(f"/{vpc_name}"):
                        gcp_subnet = self._convert_to_gcp_subnet(subnet, project_id, region)
                        subnets.append(gcp_subnet)
            else:
                # List subnets in all regions
                regions_client = compute.RegionsClient()
                regions_request = compute.ListRegionsRequest(project=project_id)
                regions_list = regions_client.list(request=regions_request)
                
                for region_obj in regions_list:
                    region_name = region_obj.name
                    
                    request = compute.ListSubnetworksRequest(
                        project=project_id,
                        region=region_name
                    )
                    subnet_list = client.list(request=request)
                    
                    for subnet in subnet_list:
                        if not vpc_name or subnet.network.endswith(f"/{vpc_name}"):
                            gcp_subnet = self._convert_to_gcp_subnet(subnet, project_id, region_name)
                            subnets.append(gcp_subnet)
            
            return subnets
            
        except Exception as e:
            raise GCPError(f"Failed to list subnets in project '{project_id}': {str(e)}")
    
    def get_subnet(
        self,
        subnet_name: str,
        region: str,
        project_id: Optional[str] = None
    ) -> GCPSubnet:
        """
        Get detailed information about a specific subnet.
        
        Args:
            subnet_name: Subnet name
            region: Region where subnet is located
            project_id: GCP project ID (uses default if not provided)
            
        Returns:
            GCPSubnet instance
            
        Raises:
            GCPValidationError: If parameters are invalid
            GCPResourceError: If subnet not found
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        validate_subnet_name(subnet_name)
        validate_region(region)
        
        try:
            client = self.client_manager.get_subnet_client()
            
            request = compute.GetSubnetworkRequest(
                project=project_id,
                region=region,
                subnetwork=subnet_name
            )
            subnet = client.get(request=request)
            
            return self._convert_to_gcp_subnet(subnet, project_id, region)
            
        except Exception as e:
            raise GCPResourceError(
                f"Failed to get subnet '{subnet_name}' in region '{region}' "
                f"for project '{project_id}': {str(e)}"
            )
    
    def create_subnet(
        self,
        subnet_name: str,
        vpc_name: str,
        cidr_range: str,
        region: str,
        project_id: Optional[str] = None,
        description: str = "",
        private_ip_google_access: bool = False,
        secondary_ranges: Optional[List[Dict[str, str]]] = None
    ) -> GCPSubnet:
        """
        Create a new subnet in a VPC network.
        
        Args:
            subnet_name: Name for the subnet
            vpc_name: VPC network name
            cidr_range: CIDR range for the subnet (e.g., "10.0.1.0/24")
            region: Region for the subnet
            project_id: GCP project ID (uses default if not provided)
            description: Description for the subnet
            private_ip_google_access: Enable private Google access
            secondary_ranges: List of secondary IP ranges
            
        Returns:
            Created GCPSubnet instance
            
        Raises:
            GCPValidationError: If parameters are invalid
            GCPResourceError: If creation fails
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        validate_subnet_name(subnet_name)
        validate_cidr_range(cidr_range)
        validate_region(region)
        
        # Normalize the subnet name
        normalized_name = normalize_resource_name(subnet_name)
        
        try:
            client = self.client_manager.get_subnet_client()
            
            # Create VPC network URL
            network_url = f"projects/{project_id}/global/networks/{vpc_name}"
            
            # Create subnet configuration
            subnet_body = compute.Subnetwork(
                name=normalized_name,
                description=description,
                network=network_url,
                ip_cidr_range=cidr_range,
                private_ip_google_access=private_ip_google_access
            )
            
            # Add secondary ranges if provided
            if secondary_ranges:
                subnet_body.secondary_ip_ranges = []
                for secondary_range in secondary_ranges:
                    secondary_ip_range = compute.SubnetworkSecondaryRange(
                        range_name=secondary_range.get('range_name'),
                        ip_cidr_range=secondary_range.get('ip_cidr_range')
                    )
                    subnet_body.secondary_ip_ranges.append(secondary_ip_range)
            
            request = compute.InsertSubnetworkRequest(
                project=project_id,
                region=region,
                subnetwork_resource=subnet_body
            )
            
            # Create the subnet
            operation = client.insert(request=request)
            
            # Wait for operation to complete
            self._wait_for_operation(operation, project_id, region)
            
            # Return the created subnet
            return self.get_subnet(normalized_name, region, project_id)
            
        except Exception as e:
            raise GCPResourceError(
                f"Failed to create subnet '{subnet_name}' in region '{region}' "
                f"for project '{project_id}': {str(e)}"
            )
    
    def update_subnet(
        self,
        subnet_name: str,
        region: str,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        private_ip_google_access: Optional[bool] = None
    ) -> GCPSubnet:
        """
        Update an existing subnet.
        
        Args:
            subnet_name: Subnet name
            region: Region where subnet is located
            project_id: GCP project ID (uses default if not provided)
            description: New description
            private_ip_google_access: New private Google access setting
            
        Returns:
            Updated GCPSubnet instance
            
        Raises:
            GCPValidationError: If parameters are invalid
            GCPResourceError: If update fails
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        validate_subnet_name(subnet_name)
        validate_region(region)
        
        try:
            client = self.client_manager.get_subnet_client()
            
            # Get current subnet
            current_subnet = self.get_subnet(subnet_name, region, project_id)
            
            # Create update configuration
            subnet_body = compute.Subnetwork(
                name=subnet_name,
                description=description if description is not None else current_subnet.description,
                network=f"projects/{project_id}/global/networks/{current_subnet.vpc_name}",
                ip_cidr_range=current_subnet.cidr_range,
                private_ip_google_access=(
                    private_ip_google_access 
                    if private_ip_google_access is not None 
                    else current_subnet.private_ip_google_access
                )
            )
            
            request = compute.PatchSubnetworkRequest(
                project=project_id,
                region=region,
                subnetwork=subnet_name,
                subnetwork_resource=subnet_body
            )
            
            # Update the subnet
            operation = client.patch(request=request)
            
            # Wait for operation to complete
            self._wait_for_operation(operation, project_id, region)
            
            # Return the updated subnet
            return self.get_subnet(subnet_name, region, project_id)
            
        except Exception as e:
            raise GCPResourceError(
                f"Failed to update subnet '{subnet_name}' in region '{region}' "
                f"for project '{project_id}': {str(e)}"
            )
    
    def delete_subnet(
        self,
        subnet_name: str,
        region: str,
        project_id: Optional[str] = None
    ) -> bool:
        """
        Delete a subnet.
        
        Args:
            subnet_name: Subnet name
            region: Region where subnet is located
            project_id: GCP project ID (uses default if not provided)
            
        Returns:
            True if deletion was successful
            
        Raises:
            GCPValidationError: If parameters are invalid
            GCPResourceError: If deletion fails
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        validate_subnet_name(subnet_name)
        validate_region(region)
        
        try:
            client = self.client_manager.get_subnet_client()
            
            request = compute.DeleteSubnetworkRequest(
                project=project_id,
                region=region,
                subnetwork=subnet_name
            )
            
            # Delete the subnet
            operation = client.delete(request=request)
            
            # Wait for operation to complete
            self._wait_for_operation(operation, project_id, region)
            
            logger.info(
                f"Subnet '{subnet_name}' deleted successfully from region '{region}' "
                f"in project '{project_id}'"
            )
            return True
            
        except Exception as e:
            raise GCPResourceError(
                f"Failed to delete subnet '{subnet_name}' in region '{region}' "
                f"for project '{project_id}': {str(e)}"
            )
    
    def _convert_to_gcp_subnet(
        self,
        subnet: compute.Subnetwork,
        project_id: str,
        region: str
    ) -> GCPSubnet:
        """
        Convert GCP API subnet object to GCPSubnet instance.
        
        Args:
            subnet: GCP API subnet object
            project_id: GCP project ID
            region: Region name
            
        Returns:
            GCPSubnet instance
        """
        # Extract VPC name from network URL
        vpc_name = subnet.network.split('/')[-1] if subnet.network else ""
        
        # Extract secondary ranges
        secondary_ranges = []
        if hasattr(subnet, 'secondary_ip_ranges') and subnet.secondary_ip_ranges:
            for secondary_range in subnet.secondary_ip_ranges:
                secondary_ranges.append({
                    'range_name': secondary_range.range_name,
                    'ip_cidr_range': secondary_range.ip_cidr_range
                })
        
        return GCPSubnet(
            id=subnet.name,
            name=subnet.name,
            status=getattr(subnet, 'status', 'READY'),
            resource_type="subnet",
            vpc_name=vpc_name,
            region=region,
            project_id=project_id,
            ip_cidr_range=subnet.ip_cidr_range,
            private_ip_google_access=getattr(subnet, 'private_ip_google_access', False),
            secondary_ip_ranges=secondary_ranges,
            created_time=subnet.creation_timestamp,
            metadata={
                'self_link': subnet.self_link,
                'description': subnet.description or ""
            }
        )
    
    def _wait_for_operation(self, operation, project_id: str, region: str, timeout: int = 300):
        """
        Wait for a regional GCP operation to complete.
        
        Args:
            operation: GCP operation object
            project_id: GCP project ID
            region: Region name
            timeout: Timeout in seconds
            
        Raises:
            GCPResourceError: If operation fails or times out
        """
        try:
            # For regional operations, use regional operations client
            operations_client = compute.RegionOperationsClient()
            
            operation_name = operation.name
            
            # Wait for operation to complete
            result = operations_client.wait(
                project=project_id,
                region=region,
                operation=operation_name,
                timeout=timeout
            )
            
            if result.error:
                error_details = []
                for error in result.error.errors:
                    error_details.append(f"{error.code}: {error.message}")
                raise GCPResourceError(f"Operation failed: {'; '.join(error_details)}")
            
        except Exception as e:
            if "Operation failed" in str(e):
                raise
            raise GCPResourceError(f"Failed to wait for operation: {str(e)}")


# Global subnet manager instance
_subnet_manager: Optional[SubnetManager] = None


def get_subnet_manager(client_manager: Optional[GCPClientManager] = None) -> SubnetManager:
    """
    Get global subnet manager instance.
    
    Args:
        client_manager: Optional client manager
        
    Returns:
        SubnetManager instance
    """
    global _subnet_manager
    if _subnet_manager is None or client_manager is not None:
        _subnet_manager = SubnetManager(client_manager)
    return _subnet_manager
