import os
import logging
import requests
from my_cli_agent.models import ToolResult
from typing import Dict, Any, List

def _call_gcloud_mcp(tool_name: str, params: Dict[str, Any]) -> ToolResult:
    """Helper function to send a command to the gcloud MCP server."""
    server_url = os.getenv("GCLOUD_MCP_SERVER_URL")
    if not server_url:
        return ToolResult(
            success=False,
            error_message="GCLOUD_MCP_SERVER_URL environment variable is not set. gcloud tools are disabled."
        )

    if not server_url.endswith('/mcp'):
        if not server_url.endswith('/'):
            server_url += '/'
        server_url += 'mcp'

    headers = {"Content-Type": "application/json"}
    payload = {
        "tool": tool_name,
        "params": params
    }

    try:
        response = requests.post(server_url, json=payload, headers=headers, timeout=120) # 2-minute timeout for potentially long commands
        response.raise_for_status()
        return ToolResult(success=True, result=response.text)
    except requests.exceptions.Timeout:
        return ToolResult(success=False, error_message="The request to the gcloud MCP server timed out (120 seconds).")
    except requests.exceptions.RequestException as e:
        return ToolResult(success=False, error_message=f"Failed to connect to the gcloud MCP server: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred calling gcloud MCP: {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred: {e}")

def run_gcloud_command(command: List[str]) -> ToolResult:
    """
    Executes a gcloud command via the gcloud-mcp server.
    The command should be provided as a list of strings.
    Example: ['compute', 'instances', 'list']
    """
    if not isinstance(command, list):
        return ToolResult(success=False, error_message="Invalid input: command must be a list of strings.")
    # The MCP server itself expects the parameter to be named 'args', so we map it here.
    return _call_gcloud_mcp("run_gcloud_command", {"args": command})
