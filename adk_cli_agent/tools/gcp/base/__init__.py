"""
Base modules for GCP ADK implementation.
"""

from .tool_context import ToolContext
from .base_agent import BaseGCPAgent, SpecializedGCPAgent
from .session_service import ADKSessionService
from .runner import ADKRunner
from .client import (
    get_gcp_client,
    get_project_id,
    set_project_id,
    clear_client_cache,
    check_authentication,
    execute_gcloud_command,
    GCPClientManager
)

# Alias for backwards compatibility
GCPClient = GCPClientManager
from .exceptions import (
    GCPToolsError,
    GCPAuthenticationError,
    GCPProjectError,
    GCPComputeError,
    GCPNetworkingError,
    GCPStorageError,
    GCPIAMError,
    GCPMonitoringError,
    GCPConfigurationError,
    GCPPermissionError,
    GCPResourceNotFoundError,
    GCPResourceConflictError
)

# Aliases for backward compatibility
BaseAgent = BaseGCPAgent
SpecializedAgent = SpecializedGCPAgent
SessionService = ADKSessionService

__all__ = [
    'ToolContext',
    'BaseGCPAgent',
    'SpecializedGCPAgent', 
    'BaseAgent',
    'SpecializedAgent',
    'ADKSessionService',
    'SessionService',
    'ADKRunner',
    'get_gcp_client',
    'get_project_id',
    'set_project_id',
    'clear_client_cache',
    'check_authentication',
    'execute_gcloud_command',
    'GCPClientManager',
    'GCPClient',
    'GCPToolsError',
    'GCPAuthenticationError',
    'GCPProjectError',
    'GCPComputeError',
    'GCPNetworkingError',
    'GCPStorageError',
    'GCPIAMError',
    'GCPMonitoringError',
    'GCPConfigurationError',
    'GCPPermissionError',
    'GCPResourceNotFoundError',
    'GCPResourceConflictError'
]