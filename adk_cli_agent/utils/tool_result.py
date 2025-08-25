"""Tool result class for standardizing responses from tool functions."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """Standardized result container for tool function returns.
    
    This class provides a consistent way to return results from tool functions,
    including success/failure status, messages, and any relevant data.
    
    Args:
        success: Boolean indicating if the operation was successful
        message: Human-readable message describing the result
        data: Optional data returned by the operation
        error_code: Optional error code for programmatic error handling
        metadata: Optional additional metadata about the operation
    """
    success: bool
    message: str = ""
    data: Any = None
    error_code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the ToolResult to a dictionary.
        
        Returns:
            Dict containing the ToolResult attributes
        """
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'error_code': self.error_code,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolResult':
        """Create a ToolResult from a dictionary.
        
        Args:
            data: Dictionary containing ToolResult attributes
            
        Returns:
            A new ToolResult instance
        """
        return cls(
            success=data.get('success', False),
            message=data.get('message', ''),
            data=data.get('data'),
            error_code=data.get('error_code'),
            metadata=data.get('metadata', {})
        )
    
    def __str__(self) -> str:
        """Return a string representation of the ToolResult."""
        status = "SUCCESS" if self.success else "ERROR"
        parts = [
            f"ToolResult({status}): {self.message}",
            f"Data: {self.data}" if self.data else "",
            f"Error Code: {self.error_code}" if self.error_code else "",
            f"Metadata: {self.metadata}" if self.metadata else ""
        ]
        return "\n".join(filter(None, parts))
