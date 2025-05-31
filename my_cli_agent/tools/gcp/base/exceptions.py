"""Custom exceptions for GCP tools."""


class GCPToolsError(Exception):
    """Base exception for all GCP tools errors."""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.error_code = error_code


class GCPAuthenticationError(GCPToolsError):
    """Raised when authentication or authorization fails."""
    
    def __init__(self, message: str = "GCP authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class GCPPermissionError(GCPToolsError):
    """Raised when user lacks necessary permissions."""
    
    def __init__(self, message: str = "Insufficient permissions for GCP operation"):
        super().__init__(message, "PERMISSION_ERROR")


class GCPResourceNotFoundError(GCPToolsError):
    """Raised when a requested resource doesn't exist."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} '{resource_id}' not found"
        super().__init__(message, "RESOURCE_NOT_FOUND")


class GCPResourceAlreadyExistsError(GCPToolsError):
    """Raised when trying to create a resource that already exists."""
    
    def __init__(self, resource_type: str, resource_id: str):
        message = f"{resource_type} '{resource_id}' already exists"
        super().__init__(message, "RESOURCE_EXISTS")


class GCPQuotaExceededError(GCPToolsError):
    """Raised when GCP quota or limits are exceeded."""
    
    def __init__(self, message: str = "GCP quota exceeded"):
        super().__init__(message, "QUOTA_EXCEEDED")


class GCPValidationError(GCPToolsError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class GCPConfigurationError(GCPToolsError):
    """Raised when GCP configuration is invalid or missing."""
    
    def __init__(self, message: str = "GCP configuration error"):
        super().__init__(message, "CONFIG_ERROR")


class GCPOperationError(GCPToolsError):
    """Raised when a GCP operation fails."""
    
    def __init__(self, operation: str, resource_type: str, message: str = ""):
        if not message:
            message = f"Failed to {operation} {resource_type}"
        super().__init__(message, "OPERATION_ERROR")
        self.operation = operation
        self.resource_type = resource_type


class GCPTimeoutError(GCPToolsError):
    """Raised when a GCP operation times out."""
    
    def __init__(self, operation: str, timeout: int):
        message = f"Operation '{operation}' timed out after {timeout} seconds"
        super().__init__(message, "TIMEOUT_ERROR")
        self.operation = operation
        self.timeout = timeout
