import os
import logging
import requests
from my_cli_agent.models import ToolResult

def call_sequential_thinking_server(prompt: str) -> ToolResult:
    """
    Sends a prompt to the Sequential Thinking MCP server for problems
    that require step-by-step reasoning or complex analysis.

    Args:
        prompt: The full user prompt detailing the problem to be solved.

    Returns:
        A ToolResult object containing the structured thought process from
        the server or an error message.
    """
    server_url = os.getenv("SEQ_THINKING_MCP_SERVER_URL")
    if not server_url:
        return ToolResult(
            success=False,
            error_message="SEQ_THINKING_MCP_SERVER_URL environment variable is not set. This tool is disabled."
        )

    if not server_url.endswith('/'):
        server_url += '/'

    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}

    try:
        response = requests.post(server_url, json=payload, headers=headers, timeout=90) # 90-second timeout
        response.raise_for_status()

        response_data = response.json()
        # Assuming the server returns the main content in a 'response' key
        result_text = response_data.get("response", "Received an empty or malformed response from the Sequential Thinking server.")
        
        return ToolResult(success=True, result=result_text)

    except requests.exceptions.Timeout:
        logging.warning("Request to Sequential Thinking MCP server timed out.")
        return ToolResult(success=False, error_message="The request to the Sequential Thinking server timed out (90 seconds).")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error calling Sequential Thinking MCP server: {e}")
        error_details = f"Failed to connect to the Sequential Thinking server at {server_url}. Details: {e}"
        return ToolResult(success=False, error_message=error_details)
    except Exception as e:
        logging.error(f"An unexpected error occurred while calling Sequential Thinking server: {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred: {e}")
