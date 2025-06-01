"""
Custom exceptions for GCP tools and agents.
"""


class GCPToolsError(Exception):
    """Base exception for GCP tools operations."""
    
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class GCPAuthenticationError(GCPToolsError):
    """Raised when GCP authentication fails."""
    pass


class GCPProjectError(GCPToolsError):
    """Raised when GCP project operations fail."""
    pass


class GCPComputeError(GCPToolsError):
    """Raised when GCP compute operations fail."""
    pass


class GCPNetworkingError(GCPToolsError):
    """Raised when GCP networking operations fail."""
    pass


class GCPStorageError(GCPToolsError):
    """Raised when GCP storage operations fail."""
    pass


class GCPIAMError(GCPToolsError):
    """Raised when GCP IAM operations fail."""
    pass


class GCPMonitoringError(GCPToolsError):
    """Raised when GCP monitoring operations fail."""
    pass


class GCPConfigurationError(GCPToolsError):
    """Raised when GCP configuration is invalid."""
    pass


class GCPPermissionError(GCPToolsError):
    """Raised when GCP permission is insufficient."""
    pass


class GCPResourceNotFoundError(GCPToolsError):
    """Raised when GCP resource is not found."""
    pass


class GCPResourceConflictError(GCPToolsError):
    """Raised when GCP resource conflicts with existing resources."""
    pass
