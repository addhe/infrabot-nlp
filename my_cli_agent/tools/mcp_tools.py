import os
import logging
import requests
from my_cli_agent.models import ToolResult

def call_mcp_server(prompt: str) -> ToolResult:
    """
    Sends a prompt to the Zen MCP server for advanced processing.

    This tool acts as a gateway to the MCP server, allowing it to handle
    complex, multi-step tasks like code reviews, debugging, and planning.

    Args:
        prompt: The full user prompt to be sent to the MCP server.

    Returns:
        A ToolResult object containing the response from the MCP server or an error.
    """
    mcp_url = os.getenv("MCP_SERVER_URL")
    if not mcp_url:
        return ToolResult(
            success=False,
            error_message="MCP_SERVER_URL environment variable is not set. This tool is disabled."
        )

    # Ensure the URL is well-formed
    if not mcp_url.endswith('/'):
        mcp_url += '/'

    headers = {"Content-Type": "application/json"}
    # The MCP server expects a simple JSON payload with the prompt
    payload = {"prompt": prompt}

    try:
        response = requests.post(mcp_url, json=payload, headers=headers, timeout=120) # 2-minute timeout for complex tasks
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Assuming the MCP server returns a JSON with a 'response' key
        response_data = response.json()
        mcp_response = response_data.get("response", "Received an empty response from MCP server.")
        
        return ToolResult(success=True, result=mcp_response)

    except requests.exceptions.Timeout:
        logging.error("Request to MCP server timed out.")
        return ToolResult(success=False, error_message="The request to the MCP server timed out (120 seconds).")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling MCP server: {e}")
        error_details = f"Failed to connect to the MCP server at {mcp_url}. Details: {e}"
        return ToolResult(success=False, error_message=error_details)
    except Exception as e:
        logging.error(f"An unexpected error occurred while calling MCP server: {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred: {e}")
