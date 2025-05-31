"""
GCP Base Module

This module provides foundational components for GCP infrastructure management,
including data types, exceptions, utilities, and client management.
"""

from .types import (
    GCPResource,
    GCPProject,
    GCPVPC,
    GCPSubnet,
    GCPOperation,
    GCPResourceStatus,
    GCPRegion
)

from .exceptions import (
    GCPToolsError,
    GCPAuthenticationError,
    GCPPermissionError,
    GCPResourceNotFoundError,
    GCPResourceAlreadyExistsError,
    GCPQuotaExceededError,
    GCPValidationError,
    GCPConfigurationError,
    GCPOperationError,
    GCPTimeoutError
)

from .utils import (
    validate_project_id,
    validate_vpc_name,
    validate_subnet_name,
    validate_cidr_range,
    validate_region,
    validate_zone,
    normalize_resource_name,
    get_default_project_id,
    format_resource_name,
    parse_labels,
    sanitize_error_message
)

from .client import (
    GCPClientManager,
    get_client_manager,
    set_default_project
)

__all__ = [
    # Types
    'GCPResource',
    'GCPProject',
    'GCPVPC',
    'GCPSubnet',
    'GCPOperation',
    'GCPResourceStatus',
    'GCPRegion',
    
    # Exceptions
    'GCPToolsError',
    'GCPAuthenticationError',
    'GCPPermissionError',
    'GCPResourceNotFoundError',
    'GCPResourceAlreadyExistsError',
    'GCPQuotaExceededError',
    'GCPValidationError',
    'GCPConfigurationError',
    'GCPOperationError',
    'GCPTimeoutError',
    
    # Utilities
    'validate_project_id',
    'validate_vpc_name',
    'validate_subnet_name',
    'validate_cidr_range',
    'validate_region',
    'validate_zone',
    'normalize_resource_name',
    'get_default_project_id',
    'format_resource_name',
    'parse_labels',
    'sanitize_error_message',
    
    # Client Management
    'GCPClientManager',
    'get_client_manager',
    'set_default_project'
]
