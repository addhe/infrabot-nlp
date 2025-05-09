from .base import ToolResult
from .time_tools import get_current_time
from .terminal_tools import execute_command

# Import GCP tools if available
try:
    from .gcp_tools import list_gcp_projects, create_gcp_project, delete_gcp_project
    HAS_GCP_TOOLS = True
except ImportError:
    # Define dummy functions if GCP tools are not available
    def list_gcp_projects(env: str) -> ToolResult:
        return ToolResult(
            success=False,
            result=None,
            error_message="GCP tools are not available. Please install the required packages: google-cloud-resource-manager, google-auth"
        )
        
    def create_gcp_project(args: str) -> ToolResult:
        return ToolResult(
            success=False,
            result=None,
            error_message="GCP tools are not available. Please install the required packages: google-cloud-resource-manager, google-auth"
        )
        
    def delete_gcp_project(args: str) -> ToolResult:
        return ToolResult(
            success=False,
            result=None,
            error_message="GCP tools are not available. Please install the required packages: google-cloud-resource-manager, google-auth"
        )
        
    HAS_GCP_TOOLS = False

__all__ = ['ToolResult', 'list_gcp_projects', 'create_gcp_project', 'delete_gcp_project', 'get_current_time', 'execute_command', 'HAS_GCP_TOOLS']