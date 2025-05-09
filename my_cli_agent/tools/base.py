from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ToolResult:
    """Represents the result of a tool execution."""
    success: bool
    result: Any
    error_message: Optional[str] = None