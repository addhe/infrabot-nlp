"""
GCP Toofrom .base import (
    # Core Types  
    GCPResource,
       # Core Types
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
    'GCPTimeoutError',source',
    'GCPProject',
    'GCPVPC', 
    'GCPSubnet',
    'GCPOperation',
    'GCPResourceStatus',
    'GCPRegion',ect,
    GCPVPC,
    GCPSubnet,
    GCPOperation,
    GCPResourceStatus,
    GCPRegion,

This module provides a comprehensive set of tools for managing Google Cloud Platform
infrastructure including projects, networking, compute, storage, and more.

This is the new modular architecture that replaces the monolithic gcp_tools.py
with a clean, service-based approach for better maintainability and extensibility.
"""

# Base components
from .base import (
    # Types
    GCPResource,
    GCPProject,
    GCPVPC,
    GCPSubnet,
    GCPOperation,
    GCPResourceStatus,
    GCPRegion,
    
    # Exceptions
    GCPToolsError,
    GCPAuthenticationError,
    GCPPermissionError,
    GCPResourceNotFoundError,
    GCPResourceAlreadyExistsError,
    GCPQuotaExceededError,
    GCPValidationError,
    GCPConfigurationError,
    GCPOperationError,
    GCPTimeoutError,
    
    # Utilities
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
    sanitize_error_message,
    
    # Client Management
    GCPClientManager,
    get_client_manager,
    set_default_project
)

# Management services
from .management import (
    ProjectManager,
    get_project_manager,
    get_mock_projects
)

# Networking services
from .networking import (
    VPCManager,
    get_vpc_manager,
    SubnetManager,
    get_subnet_manager
)

__all__ = [
    # Base Types
    'GCPResource',
    'GCPProject',
    'GCPVPC',
    'GCPSubnet',
    'GCPComputeInstance',
    'GCPStorageBucket',
    'ResourceState',
    
    # Base Exceptions
    'GCPError',
    'GCPAuthenticationError',
    'GCPClientError',
    'GCPResourceError',
    'GCPValidationError',
    'GCPOperationError',
    
    # Base Utilities
    'validate_project_id',
    'validate_vpc_name',
    'validate_subnet_name',
    'validate_cidr_range',
    'validate_region',
    'validate_zone',
    'normalize_resource_name',
    'parse_resource_url',
    'format_resource_labels',
    
    # Base Client Management
    'GCPClientManager',
    'get_client_manager',
    'set_default_project',
    
    # Management Services
    'ProjectManager',
    'get_project_manager',
    'get_mock_projects',
    
    # Networking Services
    'VPCManager',
    'get_vpc_manager',
    'SubnetManager',
    'get_subnet_manager'
]

# Version info
__version__ = "2.0.0"
__author__ = "Infrabot NLP Team"
__description__ = "Modular GCP infrastructure management tools"
