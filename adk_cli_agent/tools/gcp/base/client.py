"""
GCP Client utilities for the ADK implementation.

This module provides utilities for creating and managing GCP service clients
with proper authentication and configuration.
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from google.auth import default
from google.auth.credentials import Credentials

logger = logging.getLogger(__name__)

# Global client cache to avoid recreating clients
_client_cache: Dict[str, Any] = {}


class GCPClientManager:
    """Manages GCP service clients with authentication and caching."""
    
    def __init__(self, project_id: Optional[str] = None):
        """Initialize the client manager.
        
        Args:
            project_id: GCP project ID. If not provided, will use environment variable.
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.credentials: Optional[Credentials] = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load GCP credentials from the environment."""
        try:
            self.credentials, project = default()
            if not self.project_id:
                self.project_id = project
            logger.info(f"Successfully loaded GCP credentials for project: {self.project_id}")
        except Exception as e:
            logger.warning(f"Failed to load GCP credentials: {e}")
            self.credentials = None
    
    def get_project_id(self) -> Optional[str]:
        """Get the current project ID."""
        return self.project_id
    
    def set_project_id(self, project_id: str):
        """Set the project ID."""
        self.project_id = project_id
        # Clear client cache when project changes
        _client_cache.clear()
    
    def has_credentials(self) -> bool:
        """Check if valid credentials are available."""
        return self.credentials is not None
    
    def get_credentials(self) -> Optional[Credentials]:
        """Get the current credentials."""
        return self.credentials


# Global client manager instance
_client_manager = GCPClientManager()


def get_gcp_client(service_name: str, version: str = 'v1', **kwargs) -> Any:
    """Get a GCP service client with caching.
    
    Args:
        service_name: Name of the GCP service (e.g., 'compute', 'storage')
        version: API version to use
        **kwargs: Additional arguments for client creation
        
    Returns:
        GCP service client instance
        
    Raises:
        GCPClientError: If client creation fails
    """
    from .exceptions import GCPToolsError
    
    cache_key = f"{service_name}_{version}_{_client_manager.project_id}"
    
    # Return cached client if available
    if cache_key in _client_cache:
        return _client_cache[cache_key]
    
    if not _client_manager.has_credentials():
        raise GCPToolsError(
            "No valid GCP credentials found. Please set up authentication."
        )
    
    try:
        # Import the appropriate client library
        if service_name == 'compute':
            from googleapiclient import discovery
            client = discovery.build(
                service_name, 
                version, 
                credentials=_client_manager.get_credentials(),
                **kwargs
            )
        elif service_name == 'storage':
            from google.cloud import storage
            client = storage.Client(
                project=_client_manager.project_id,
                credentials=_client_manager.get_credentials()
            )
        elif service_name == 'resourcemanager':
            from googleapiclient import discovery
            client = discovery.build(
                'cloudresourcemanager', 
                'v1', 
                credentials=_client_manager.get_credentials(),
                **kwargs
            )
        elif service_name == 'iam':
            from googleapiclient import discovery
            client = discovery.build(
                service_name, 
                version, 
                credentials=_client_manager.get_credentials(),
                **kwargs
            )
        elif service_name == 'monitoring':
            from google.cloud import monitoring_v3
            client = monitoring_v3.MetricServiceClient(
                credentials=_client_manager.get_credentials()
            )
        elif service_name == 'logging':
            from google.cloud import logging as cloud_logging
            client = cloud_logging.Client(
                project=_client_manager.project_id,
                credentials=_client_manager.get_credentials()
            )
        else:
            # Generic client using discovery API
            from googleapiclient import discovery
            client = discovery.build(
                service_name, 
                version, 
                credentials=_client_manager.get_credentials(),
                **kwargs
            )
        
        # Cache the client
        _client_cache[cache_key] = client
        logger.info(f"Created and cached {service_name} client (version {version})")
        
        return client
        
    except Exception as e:
        raise GCPToolsError(f"Failed to create {service_name} client: {str(e)}")


def get_project_id() -> Optional[str]:
    """Get the current GCP project ID.
    
    Returns:
        Current project ID or None if not set
    """
    return _client_manager.get_project_id()


def set_project_id(project_id: str):
    """Set the GCP project ID.
    
    Args:
        project_id: New project ID to use
    """
    _client_manager.set_project_id(project_id)


def clear_client_cache():
    """Clear the client cache. Useful for testing or credential changes."""
    global _client_cache
    _client_cache.clear()
    logger.info("Cleared GCP client cache")


def check_authentication() -> Dict[str, Any]:
    """Check GCP authentication status.
    
    Returns:
        Dictionary with authentication status information
    """
    status = {
        'has_credentials': _client_manager.has_credentials(),
        'project_id': _client_manager.get_project_id(),
        'cached_clients': list(_client_cache.keys())
    }
    
    if _client_manager.has_credentials():
        try:
            # Test authentication by listing projects
            client = get_gcp_client('resourcemanager', 'v1')
            # This is a simple test that doesn't require specific permissions
            status['authentication_test'] = 'passed'
        except Exception as e:
            status['authentication_test'] = f'failed: {str(e)}'
    else:
        status['authentication_test'] = 'no_credentials'
    
    return status


def execute_gcloud_command(command: str, capture_output: bool = True) -> Dict[str, Any]:
    """Execute a gcloud CLI command as fallback.
    
    Args:
        command: gcloud command to execute (without 'gcloud' prefix)
        capture_output: Whether to capture and return output
        
    Returns:
        Dictionary with execution results
    """
    import subprocess
    import json
    
    full_command = f"gcloud {command}"
    
    try:
        if capture_output:
            result = subprocess.run(
                full_command.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
            
            # Try to parse JSON output
            if output['success'] and result.stdout.strip():
                try:
                    output['data'] = json.loads(result.stdout)
                except json.JSONDecodeError:
                    output['data'] = result.stdout.strip()
            
            return output
        else:
            # Execute without capturing output
            result = subprocess.run(full_command.split(), timeout=30)
            return {
                'success': result.returncode == 0,
                'return_code': result.returncode
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timed out after 30 seconds'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
