"""
GCP Client Management Module

This module provides centralized GCP client management with proper authentication,
error handling, and resource lifecycle management.
"""

from typing import Optional, Dict, Any
import logging
from google.cloud import resourcemanager
from google.cloud import compute
from google.auth import default
from google.auth.credentials import Credentials

from .exceptions import GCPAuthenticationError, GCPToolsError
from .types import GCPProject

logger = logging.getLogger(__name__)


class GCPClientManager:
    """
    Centralized GCP client management with authentication and service clients.
    
    This class manages GCP service clients with proper authentication,
    error handling, and resource lifecycle management.
    """
    
    def __init__(self, project_id: Optional[str] = None, credentials: Optional[Credentials] = None):
        """
        Initialize GCP client manager.
        
        Args:
            project_id: GCP project ID (optional, can be set from environment)
            credentials: GCP credentials (optional, will use default if not provided)
        """
        self.project_id = project_id
        self.credentials = credentials
        self._clients: Dict[str, Any] = {}
        
        # Initialize credentials if not provided
        if self.credentials is None:
            try:
                self.credentials, default_project = default()
                if self.project_id is None:
                    self.project_id = default_project
            except Exception as e:
                raise GCPAuthenticationError(f"Failed to authenticate with GCP: {str(e)}")
    
    def get_resource_manager_client(self) -> resourcemanager.ProjectsClient:
        """
        Get or create Resource Manager client.
        
        Returns:
            ResourceManager client instance
            
        Raises:
            GCPToolsError: If client creation fails
        """
        if 'resource_manager' not in self._clients:
            try:
                self._clients['resource_manager'] = resourcemanager.ProjectsClient(
                    credentials=self.credentials
                )
            except Exception as e:
                raise GCPToolsError(f"Failed to create Resource Manager client: {str(e)}")
        
        return self._clients['resource_manager']
    
    def get_compute_client(self) -> compute.InstancesClient:
        """
        Get or create Compute Engine client.
        
        Returns:
            Compute Engine client instance
            
        Raises:
            GCPToolsError: If client creation fails
        """
        if 'compute' not in self._clients:
            try:
                self._clients['compute'] = compute.InstancesClient(
                    credentials=self.credentials
                )
            except Exception as e:
                raise GCPToolsError(f"Failed to create Compute Engine client: {str(e)}")
        
        return self._clients['compute']
    
    def get_vpc_client(self) -> compute.NetworksClient:
        """
        Get or create VPC Networks client.
        
        Returns:
            VPC Networks client instance
            
        Raises:
            GCPToolsError: If client creation fails
        """
        if 'vpc' not in self._clients:
            try:
                self._clients['vpc'] = compute.NetworksClient(
                    credentials=self.credentials
                )
            except Exception as e:
                raise GCPToolsError(f"Failed to create VPC Networks client: {str(e)}")
        
        return self._clients['vpc']
    
    def get_subnet_client(self) -> compute.SubnetworksClient:
        """
        Get or create Subnet client.
        
        Returns:
            Subnet client instance
            
        Raises:
            GCPToolsError: If client creation fails
        """
        if 'subnet' not in self._clients:
            try:
                self._clients['subnet'] = compute.SubnetworksClient(
                    credentials=self.credentials
                )
            except Exception as e:
                raise GCPToolsError(f"Failed to create Subnet client: {str(e)}")
        
        return self._clients['subnet']
    
    def validate_project_access(self, project_id: Optional[str] = None) -> GCPProject:
        """
        Validate access to a GCP project.
        
        Args:
            project_id: Project ID to validate (uses default if not provided)
            
        Returns:
            GCPProject instance with project details
            
        Raises:
            GCPAuthenticationError: If project access fails
        """
        target_project = project_id or self.project_id
        if not target_project:
            raise GCPAuthenticationError("No project ID specified")
        
        try:
            client = self.get_resource_manager_client()
            project_name = f"projects/{target_project}"
            project = client.get_project(name=project_name)
            
            return GCPProject(
                id=project.project_id,
                name=project.display_name or project.project_id,
                status=project.state.name,
                resource_type="project",
                project_id=project.project_id,
                labels=dict(project.labels) if project.labels else {}
            )
        except Exception as e:
            raise GCPAuthenticationError(
                f"Failed to access project '{target_project}': {str(e)}"
            )
    
    def close(self):
        """
        Close all active clients and clean up resources.
        """
        for client_name, client in self._clients.items():
            try:
                if hasattr(client, 'close'):
                    client.close()
            except Exception as e:
                logger.warning(f"Error closing {client_name} client: {str(e)}")
        
        self._clients.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global client manager instance
_global_client_manager: Optional[GCPClientManager] = None


def get_client_manager(
    project_id: Optional[str] = None,
    credentials: Optional[Credentials] = None,
    force_new: bool = False
) -> GCPClientManager:
    """
    Get global client manager instance or create a new one.
    
    Args:
        project_id: GCP project ID
        credentials: GCP credentials
        force_new: Force creation of new client manager
        
    Returns:
        GCPClientManager instance
    """
    global _global_client_manager
    
    if force_new or _global_client_manager is None:
        _global_client_manager = GCPClientManager(project_id, credentials)
    
    return _global_client_manager


def set_default_project(project_id: str):
    """
    Set default project ID for global client manager.
    
    Args:
        project_id: GCP project ID to set as default
    """
    global _global_client_manager
    if _global_client_manager:
        _global_client_manager.project_id = project_id
