from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ToolResult:
    """
    Represents a standardized result from a tool execution.

    Attributes:
        success: A boolean indicating if the tool executed successfully.
        result: The output of the tool on success. Can be any type, but
                is typically a string for easy display.
        error_message: A string containing an error message on failure.
    """
    success: bool
    result: Optional[str] = None
    error_message: Optional[str] = None
