"""Google Cloud Platform (GCP) Service Management.

This module provides functionality to manage GCP services such as enabling/disabling
APIs and checking service status.
"""

import logging
import re
import time
from datetime import datetime, timedelta, UTC
from typing import Dict, List, Optional, Tuple, Union, Any

# Try to import Google Cloud client libraries
try:
    from google.api_core.exceptions import GoogleAPICallError, RetryError, PermissionDenied, NotFound
    from google.cloud import serviceusage_v1
    from google.cloud.serviceusage_v1 import ServiceUsageClient
    from google.cloud.serviceusage_v1.types import Service, ListServicesResponse, EnableServiceRequest, GetServiceRequest, ListServicesRequest
    from google.api_core.retry import Retry
    from google.api_core.operation import Operation
    HAS_GCP_LIBS = True
except ImportError:
    HAS_GCP_LIBS = False
    # Create mock classes when Google Cloud libraries are not available
    class ServiceUsageClient:
        def get_service(self, request):
            pass
        
        def enable_service(self, request):
            pass
        
        def list_services(self, request):
            pass
    
    class Service:
        def __init__(self, name=None, state=None):
            self.name = name
            self.state = state
            self.config = type('Config', (), {'title': 'Mock Service'})
        
        class State:
            ENABLED = 'ENABLED'
            DISABLED = 'DISABLED'
    
    class Operation:
        def result(self, timeout=None):
            pass
        
        def done(self):
            return True
    
    class ListServicesResponse:
        def __init__(self, services=None):
            self.services = services or []
    
    class EnableServiceRequest:
        def __init__(self, name=None):
            self.name = name
    
    class GetServiceRequest:
        def __init__(self, name=None):
            self.name = name
    
    class ListServicesRequest:
        def __init__(self, parent=None, filter_=None, page_size=None, page_token=None):
            self.parent = parent
            self.filter = filter_
            self.page_size = page_size
            self.page_token = page_token
    
    class GoogleAPICallError(Exception):
        pass
    
    class RetryError(Exception):
        pass
    
    class PermissionDenied(Exception):
        pass

    class NotFound(Exception):
        pass

    # Mock Retry class
    class Retry:
        def __init__(self, *args, **kwargs):
            pass
        
        def __call__(self, func):
            def wrapped(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapped.__dict__.update(kwargs)

from adk_cli_agent.utils.tool_result import ToolResult

# Setup logging
logger = logging.getLogger(__name__)

# Common GCP service names
COMMON_SERVICES = {
    'compute': 'compute.googleapis.com',
    'storage': 'storage.googleapis.com',
    'cloudresourcemanager': 'cloudresourcemanager.googleapis.com',
    'container': 'container.googleapis.com',
    'iam': 'iam.googleapis.com',
    'sqladmin': 'sqladmin.googleapis.com',
    'servicenetworking': 'servicenetworking.googleapis.com',
    'dns': 'dns.googleapis.com',
}

def _get_service_usage_client() -> 'ServiceUsageClient':
    """Initialize and return a Service Usage API client.
    
    Returns:
        ServiceUsageClient: Initialized client
        
    Raises:
        ImportError: If Google Cloud client libraries are not installed
    """
    if not HAS_GCP_LIBS:
        raise ImportError(
            "Google Cloud client libraries not found. "
            "Please install with: pip install google-cloud-service-usage"
        )
    return serviceusage_v1.ServiceUsageClient()

def is_service_enabled(project_id: str, service_name: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Check if a specific service is enabled for a project.
    
    Args:
        project_id: GCP project ID
        service_name: Name of the service to check (e.g., 'compute.googleapis.com')
        
    Returns:
        Tuple[bool, Optional[dict]]: (is_enabled, service_info)
            is_enabled: True if service is enabled
            service_info: Dictionary with service details or None if not found
            
    Example:
        >>> is_enabled, info = is_service_enabled('my-project', 'compute.googleapis.com')
        >>> print(is_enabled)  # True or False
    """
    try:
        client = _get_service_usage_client()
        service_path = f"projects/{project_id}/services/{service_name}"
        
        service = client.get_service(name=service_path)
        
        service_info = {
            'name': service.name,
            'parent': service.parent,
            'state': getattr(service, 'state', Service.State.DISABLED).name,
            'enabled': getattr(service, 'state', Service.State.DISABLED) == Service.State.ENABLED
        }
        
        return service_info['enabled'], service_info
        
    except NotFound:
        return False, None
    except GoogleAPICallError as e:
        logger.error(f"Error checking service status: {e}")
        raise

def enable_service(
    project_id: str, 
    service_name: str,
    timeout: int = 300
) -> Tuple[bool, str]:
    """Enable a service for a GCP project.
    
    Args:
        project_id: GCP project ID
        service_name: Name of the service to enable (e.g., 'compute.googleapis.com')
        timeout: Timeout in seconds to wait for the operation to complete
        
    Returns:
        Tuple[bool, str]: (success, message)
        
    Example:
        >>> success, message = enable_service('my-project', 'compute.googleapis.com')
        >>> print(success, message)  # True, 'Successfully enabled compute.googleapis.com'
    """
    try:
        client = _get_service_usage_client()
        service_path = f"projects/{project_id}/services/{service_name}"
        
        # Check current status first
        is_enabled, _ = is_service_enabled(project_id, service_name)
        if is_enabled:
            return True, f"Service {service_name} is already enabled"
            
        # Configure retry with backoff if Retry is available
        retry = None
        if HAS_GCP_LIBS:
            retry = Retry(
                initial=1.0,
                maximum=60.0,
                multiplier=2.0,
                deadline=float(timeout),
                predicate=retry_if_not_found
            )
        
        # Enable the service
        operation = client.enable_service(
            request={"name": service_path},
            retry=retry,
            timeout=timeout if HAS_GCP_LIBS else None
        )
        
        logger.info(f"Waiting for enable operation on '{service_name}' to complete...")
        # The result() method blocks until the operation is complete.
        operation.result(timeout=timeout)

        # If result() completes without raising an exception, it's a success.
        msg = f"Successfully enabled service: {service_name}"
        logger.info(msg)
        return True, msg
        
    except PermissionDenied as e:
        msg = (
            f"Permission denied when enabling {service_name}. "
            "Ensure the service account has 'roles/serviceusage.serviceUsageAdmin' role."
        )
        logger.error(f"{msg} Error: {e}")
        return False, msg
        
    except GoogleAPICallError as e:
        logger.error(f"Error enabling service {service_name}: {e}")
        return False, f"Failed to enable {service_name}: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error in enable_service: {e}")
        return False, f"Unexpected error: {str(e)}"

def list_enabled_services(project_id: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """List all enabled services for a project.
    
    Args:
        project_id: GCP project ID
        
    Returns:
        Tuple[bool, List[Dict]]: (success, services)
            success: True if the operation was successful
            services: List of enabled services with their details
            
    Example:
        >>> success, services = list_enabled_services('my-project')
        >>> if success:
        ...     for svc in services:
        ...         print(f"{svc['title']}: {svc['state']}")
    """
    try:
        client = _get_service_usage_client()
        parent = f"projects/{project_id}"
        
        # List all services, filtering for enabled ones
        request = {
            'parent': parent,
            'filter': 'state:ENABLED',
        }
        
        # For testing without Google Cloud libraries
        if not HAS_GCP_LIBS:
            mock_service = {
                'name': f"{parent}/services/compute.googleapis.com",
                'config': {'title': 'Compute Engine API'},
                'state': 'ENABLED'
            }
            return True, [mock_service]
        
        # Real implementation with Google Cloud client
        services = []
        for service in client.list_services(request=request):
            services.append({
                'name': service.name,
                'title': getattr(service.config, 'title', 'Unknown Service'),
                'state': getattr(service, 'state', 'UNKNOWN').name,
                'enabled': getattr(service, 'state', Service.State.DISABLED) == Service.State.ENABLED
            })
            
        return True, services
        
    except GoogleAPICallError as e:
        logger.error(f"Error listing enabled services: {e}")
        return False, []
    except Exception as e:
        logger.error(f"Unexpected error in list_enabled_services: {e}")
        return False, []

def retry_if_not_found(exception: Exception) -> bool:
    """Determine if a retry should be attempted based on the exception.
    
    Args:
        exception: The exception that was raised
        
    Returns:
        bool: True if a retry should be attempted
    """
    if not HAS_GCP_LIBS:
        return False
    return isinstance(exception, NotFound)

def enable_gcp_service_tool(project_id: str, service_name: str) -> ToolResult:
    """Tool function to enable a GCP service.
    
    This is the main entry point for the ADK agent to enable GCP services.
    
    Args:
        project_id: GCP project ID
        service_name: Name of the service to enable (e.g., 'compute' or 'compute.googleapis.com')
        
    Returns:
        ToolResult: Result of the operation with success status, message, and service info
        
    Example:
        >>> result = enable_gcp_service_tool('my-project', 'compute')
        >>> print(f"Success: {result.success}")
        >>> print(f"Message: {result.message}")
        >>> if result.data:
        ...     print(f"Service info: {result.data}")
    """
    if not HAS_GCP_LIBS:
        # For testing without Google Cloud libraries
        mock_service = {
            'name': f'projects/{project_id}/services/{service_name}.googleapis.com',
            'state': 'ENABLED',
            'enabled': True
        }
        return ToolResult(
            success=True,
            message=f"Mocked successful enablement of {service_name}.googleapis.com",
            data=mock_service,
            metadata={
                'mocked': True,
                'service_name': f"{service_name}.googleapis.com"
            }
        )
    
    try:
        # Handle short service names (e.g., 'compute' -> 'compute.googleapis.com')
        service_full_name = COMMON_SERVICES.get(service_name.lower(), service_name)
        if not service_full_name.endswith('.googleapis.com'):
            service_full_name = f"{service_full_name}.googleapis.com"
        
        # First check if already enabled
        is_enabled, service_info = is_service_enabled(project_id, service_full_name)
        if is_enabled:
            return ToolResult(
                success=True,
                message=f"Service {service_full_name} is already enabled",
                data=service_info,
                metadata={
                    'service_name': service_full_name,
                    'status': 'already_enabled'
                }
            )
        
        # If not enabled, enable it
        success, message = enable_service(project_id, service_full_name)
        
        if success:
            # Verify the service is now enabled
            is_enabled, service_info = is_service_enabled(project_id, service_full_name)
            if is_enabled:
                return ToolResult(
                    success=True,
                    message=f"Successfully enabled {service_full_name}",
                    data=service_info,
                    metadata={
                        'service_name': service_full_name,
                        'status': 'enabled',
                        'enabled_at': datetime.now(UTC).isoformat()
                    }
                )
            return ToolResult(
                success=False,
                message=f"Service {service_full_name} activation may not have completed successfully",
                error_code="ACTIVATION_INCOMPLETE",
                metadata={
                    'service_name': service_full_name,
                    'status': 'activation_pending'
                }
            )
        
        return ToolResult(
            success=False,
            message=message,
            error_code="SERVICE_ENABLEMENT_FAILED",
            metadata={
                'service_name': service_full_name if 'service_full_name' in locals() else service_name,
                'status': 'enablement_failed'
            }
        )
        
    except Exception as e:
        error_msg = f"Error enabling service {service_name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return ToolResult(
            success=False, 
            message=error_msg,
            error_code="UNEXPECTED_ERROR",
            metadata={
                'service_name': service_name,
                'exception_type': e.__class__.__name__,
                'status': 'error'
            }
        )


def list_gcp_services_tool(project_id: str) -> ToolResult:
    """Tool function to list all enabled GCP services for a project.
    
    This function provides a user-friendly interface to retrieve a list of all
    enabled services for a given GCP project. It handles errors gracefully and
    returns a structured result that can be easily processed by the ADK agent.
    
    Args:
        project_id: GCP project ID to list services for
        
    Returns:
        ToolResult: Contains the list of enabled services or error information
        
    Example:
        >>> result = list_gcp_services_tool('my-project')
        >>> if result.success:
        ...     print(f"Found {len(result.data)} services:")
        ...     for svc in result.data:
        ...         print(f"- {svc.get('title', 'Unknown')} ({svc.get('name', 'N/A')})")
    """
    if not HAS_GCP_LIBS:
        # Return mock data when Google Cloud libraries are not available
        mock_services = [
            {
                'name': f'projects/{project_id}/services/compute.googleapis.com',
                'title': 'Compute Engine API',
                'state': 'ENABLED',
                'enabled': True
            },
            {
                'name': f'projects/{project_id}/services/storage.googleapis.com',
                'title': 'Cloud Storage API',
                'state': 'ENABLED',
                'enabled': True
            }
        ]
        return ToolResult(
            success=True,
            message=f"Mocked list of {len(mock_services)} services (Google Cloud libraries not installed)",
            data=mock_services,
            metadata={
                'mocked': True,
                'project_id': project_id,
                'count': len(mock_services)
            }
        )
    
    try:
        success, services = list_enabled_services(project_id)
        if not success:
            return ToolResult(
                success=False,
                message="Failed to retrieve list of enabled services. "
                       "Please check your project ID and permissions.",
                error_code="SERVICE_LIST_FAILED",
                metadata={
                    'project_id': project_id,
                    'status': 'retrieval_failed'
                }
            )
            
        if not services:
            return ToolResult(
                success=True,
                message="No enabled services found for this project",
                data=[],
                error_code="NO_SERVICES_FOUND",
                metadata={
                    'project_id': project_id,
                    'status': 'no_services',
                    'count': 0
                }
            )
            
        # Sort services by title for better readability
        sorted_services = sorted(
            services,
            key=lambda x: x.get('title', '').lower()
        )
        
        return ToolResult(
            success=True,
            message=f"Found {len(sorted_services)} enabled services",
            data=sorted_services,
            metadata={
                'count': len(sorted_services),
                'project_id': project_id,
                'status': 'success',
                'timestamp': datetime.now(UTC).isoformat()
            }
        )
        
    except PermissionDenied as e:
        error_msg = (
            "Permission denied when listing services. "
            f"Ensure the service account has 'roles/serviceusage.serviceUsageViewer' role. Error: {str(e)}"
        )
        logger.error(error_msg)
        return ToolResult(
            success=False,
            message=error_msg,
            error_code="PERMISSION_DENIED",
            metadata={
                'project_id': project_id,
                'status': 'permission_denied',
                'exception_type': e.__class__.__name__
            }
        )
        
    except Exception as e:
        error_msg = f"Unexpected error listing services: {str(e)}"
        logger.exception(error_msg)  # Log full stack trace
        return ToolResult(
            success=False,
            message=error_msg,
            error_code="UNEXPECTED_ERROR",
            metadata={
                'project_id': project_id,
                'status': 'error',
                'exception_type': e.__class__.__name__
            }
        )
