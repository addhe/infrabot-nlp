import os
import logging
import requests
from my_cli_agent.models import ToolResult
from typing import Dict, Any, Optional

def call_mcp_server_helper(
    prompt: str,
    mcp_env_var: str,
    tool_name: str,
    payload: Optional[Dict[str, Any]] = None
) -> ToolResult:
    """
    A generic helper function to send a prompt to an MCP server.

    This function encapsulates the common logic for making an HTTP POST request
    to an MCP server, including configuration, error handling, and response parsing.

    Args:
        prompt: The user prompt to be sent to the MCP server.
        mcp_env_var: The name of the environment variable holding the MCP server URL.
        tool_name: The name of the tool calling this helper (for logging and error messages).
        payload: The JSON payload to send. If None, it defaults to `{"prompt": prompt}`.

    Returns:
        A ToolResult object containing the response from the MCP server or a
        descriptive error message.
    """
    mcp_url = os.getenv(mcp_env_var)
    if not mcp_url:
        error_msg = f"{mcp_env_var} environment variable is not set. The {tool_name} tool is disabled."
        logging.warning(error_msg)
        return ToolResult(success=False, error_message=error_msg)

    # Ensure the URL is well-formed for endpoint concatenation
    if not mcp_url.endswith('/'):
        mcp_url += '/'

    headers = {"Content-Type": "application/json"}

    if payload is None:
        payload = {"prompt": prompt}

    try:
        # Using a timeout for the request
        response = requests.post(mcp_url, json=payload, headers=headers, timeout=180) # 3-minute timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        response_data = response.json()
        mcp_response = response_data.get("response", f"Received an empty or malformed response from {tool_name}.")

        return ToolResult(success=True, result=mcp_response)

    except requests.exceptions.Timeout:
        error_msg = f"The request to the {tool_name} server timed out (180 seconds)."
        logging.error(error_msg)
        return ToolResult(success=False, error_message=error_msg)
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to the {tool_name} server at {mcp_url}. Details: {e}"
        logging.error(error_msg)
        return ToolResult(success=False, error_message=error_msg)
    except Exception as e:
        error_msg = f"An unexpected error occurred in the {tool_name} tool: {e}"
        logging.error(error_msg, exc_info=True)
        return ToolResult(success=False, error_message=error_msg)
