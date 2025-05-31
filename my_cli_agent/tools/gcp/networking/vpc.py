"""
GCP VPC Management Module

This module provides comprehensive VPC (Virtual Private Cloud) management
functionality including VPC creation, listing, updating, and deletion.
"""

import logging
from typing import List, Optional, Dict, Any
from google.cloud import compute_v1

from ..base import (
    GCPVPC,
    GCPClientManager,
    get_client_manager,
    GCPToolsError,
    GCPResourceNotFoundError,
    GCPValidationError,
    GCPOperationError,
    validate_project_id,
    validate_vpc_name,
    normalize_resource_name
)

# Create aliases for backward compatibility
GCPError = GCPToolsError
GCPResourceError = GCPToolsError

logger = logging.getLogger(__name__)


class VPCManager:
    """
    GCP VPC management with comprehensive CRUD operations.
    
    This class provides methods for creating, listing, updating, and deleting
    VPC networks with proper error handling and validation.
    """
    
    def __init__(self, client_manager: Optional[GCPClientManager] = None):
        """
        Initialize VPC manager.
        
        Args:
            client_manager: GCP client manager instance
        """
        self.client_manager = client_manager or get_client_manager()
    
    def list_vpcs(self, project_id: Optional[str] = None) -> List[GCPVPC]:
        """
        List all VPCs in a project.
        
        Args:
            project_id: GCP project ID (uses default if not provided)
            
        Returns:
            List of GCPVPC instances
            
        Raises:
            GCPError: If listing fails
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        
        try:
            client = self.client_manager.get_vpc_client()
            
            # List all networks in the project
            request = compute_v1.ListNetworksRequest(project=project_id)
            networks = client.list(request=request)
            
            vpcs = []
            for network in networks:
                vpc = GCPVPC(
                    project_id=project_id,
                    name=network.name,
                    description=network.description or "",
                    auto_create_subnetworks=getattr(network, 'auto_create_subnetworks', False),
                    routing_mode=getattr(network, 'routing_config', {}).get('routing_mode', 'REGIONAL'),
                    self_link=network.self_link,
                    creation_timestamp=network.creation_timestamp
                )
                vpcs.append(vpc)
            
            return vpcs
            
        except Exception as e:
            raise GCPError(f"Failed to list VPCs in project '{project_id}': {str(e)}")
    
    def get_vpc(self, vpc_name: str, project_id: Optional[str] = None) -> GCPVPC:
        """
        Get detailed information about a specific VPC.
        
        Args:
            vpc_name: VPC network name
            project_id: GCP project ID (uses default if not provided)
            
        Returns:
            GCPVPC instance
            
        Raises:
            GCPValidationError: If parameters are invalid
            GCPResourceError: If VPC not found
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        validate_vpc_name(vpc_name)
        
        try:
            client = self.client_manager.get_vpc_client()
            
            request = compute_v1.GetNetworkRequest(
                project=project_id,
                network=vpc_name
            )
            network = client.get(request=request)
            
            return GCPVPC(
                project_id=project_id,
                name=network.name,
                description=network.description or "",
                auto_create_subnetworks=getattr(network, 'auto_create_subnetworks', False),
                routing_mode=getattr(network, 'routing_config', {}).get('routing_mode', 'REGIONAL'),
                self_link=network.self_link,
                creation_timestamp=network.creation_timestamp
            )
            
        except Exception as e:
            raise GCPResourceError(f"Failed to get VPC '{vpc_name}' in project '{project_id}': {str(e)}")
    
    def create_vpc(
        self,
        vpc_name: str,
        project_id: Optional[str] = None,
        description: str = "",
        auto_create_subnetworks: bool = False,
        routing_mode: str = "REGIONAL"
    ) -> GCPVPC:
        """
        Create a new VPC network.
        
        Args:
            vpc_name: Name for the VPC
            project_id: GCP project ID (uses default if not provided)
            description: Description for the VPC
            auto_create_subnetworks: Whether to auto-create subnets
            routing_mode: Routing mode (REGIONAL or GLOBAL)
            
        Returns:
            Created GCPVPC instance
            
        Raises:
            GCPValidationError: If parameters are invalid
            GCPResourceError: If creation fails
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        validate_vpc_name(vpc_name)
        
        # Normalize the VPC name
        normalized_name = normalize_resource_name(vpc_name)
        
        try:
            client = self.client_manager.get_vpc_client()
            
            # Create network configuration
            network_body = compute_v1.Network(
                name=normalized_name,
                description=description,
                auto_create_subnetworks=auto_create_subnetworks,
                routing_config=compute_v1.NetworkRoutingConfig(
                    routing_mode=routing_mode
                )
            )
            
            request = compute_v1.InsertNetworkRequest(
                project=project_id,
                network_resource=network_body
            )
            
            # Create the network
            operation = client.insert(request=request)
            
            # Wait for operation to complete
            self._wait_for_operation(operation, project_id)
            
            # Return the created VPC
            return self.get_vpc(normalized_name, project_id)
            
        except Exception as e:
            raise GCPResourceError(f"Failed to create VPC '{vpc_name}' in project '{project_id}': {str(e)}")
    
    def update_vpc(
        self,
        vpc_name: str,
        project_id: Optional[str] = None,
        description: Optional[str] = None,
        routing_mode: Optional[str] = None
    ) -> GCPVPC:
        """
        Update an existing VPC network.
        
        Args:
            vpc_name: VPC network name
            project_id: GCP project ID (uses default if not provided)
            description: New description
            routing_mode: New routing mode
            
        Returns:
            Updated GCPVPC instance
            
        Raises:
            GCPValidationError: If parameters are invalid
            GCPResourceError: If update fails
        """
        project_id = project_id or self.client_manager.project_id
        if not project_id:
            raise GCPValidationError("Project ID is required")
        
        validate_project_id(project_id)
        validate_vpc_name(vpc_name)
        
        try:
            client = self.client_manager.get_vpc_client()
            
            # Get current network
            current_vpc = self.get_vpc(vpc_name, project_id)
            
            # Create update configuration
            network_body = compute_v1.Network(
                name=vpc_name,
                description=description if description is not None else current_vpc.description,
                auto_create_subnetworks=current_vpc.auto_create_subnetworks
            )
            
            if routing_mode is not None:
                network_body.routing_config = compute_v1.NetworkRoutingConfig(
                    routing_mode=routing_mode
                )
            
            request = compute_v1.PatchNetworkRequest(
                project=project_id,
                network=vpc_name,
                network_resource=network_body
            )
            
            # Update the network
            operation = client.patch(request=request)
            
            # Wait for operation to complete
            self._wait_for_operation(operation, project_id)
            
            # Return the updated VPC
            return self.get_vpc(vpc_name, project_id)
            
        except Exception as e:
            raise GCPResourceError(f"Failed to update VPC '{vpc_name}' in project '{project_id}': {str(e)}")
    
    def delete_vpc(self, vpc_name: str, project_id: Optional[str] = None) -> bool:
        """
        Delete a VPC network.
        
        Args:
            vpc_name: VPC network name
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
        validate_vpc_name(vpc_name)
        
        try:
            client = self.client_manager.get_vpc_client()
            
            request = compute_v1.DeleteNetworkRequest(
                project=project_id,
                network=vpc_name
            )
            
            # Delete the network
            operation = client.delete(request=request)
            
            # Wait for operation to complete
            self._wait_for_operation(operation, project_id)
            
            logger.info(f"VPC '{vpc_name}' deleted successfully from project '{project_id}'")
            return True
            
        except Exception as e:
            raise GCPResourceError(f"Failed to delete VPC '{vpc_name}' in project '{project_id}': {str(e)}")
    
    def _wait_for_operation(self, operation, project_id: str, timeout: int = 300):
        """
        Wait for a GCP operation to complete.
        
        Args:
            operation: GCP operation object
            project_id: GCP project ID
            timeout: Timeout in seconds
            
        Raises:
            GCPResourceError: If operation fails or times out
        """
        try:
            # For global operations, use global operations client
            operations_client = compute_v1.GlobalOperationsClient()
            
            operation_name = operation.name
            
            # Wait for operation to complete
            result = operations_client.wait(
                project=project_id,
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


# Global VPC manager instance
_vpc_manager: Optional[VPCManager] = None


def get_vpc_manager(client_manager: Optional[GCPClientManager] = None) -> VPCManager:
    """
    Get global VPC manager instance.
    
    Args:
        client_manager: Optional client manager
        
    Returns:
        VPCManager instance
    """
    global _vpc_manager
    if _vpc_manager is None or client_manager is not None:
        _vpc_manager = VPCManager(client_manager)
    return _vpc_manager
