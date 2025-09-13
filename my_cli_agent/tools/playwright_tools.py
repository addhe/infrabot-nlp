import os
import logging
import requests
from my_cli_agent.models import ToolResult
from typing import Dict, Any

def _call_playwright_mcp(tool_name: str, params: Dict[str, Any]) -> ToolResult:
    """Helper function to send a command to the Playwright MCP server."""
    server_url = os.getenv("PLAYWRIGHT_MCP_SERVER_URL")
    if not server_url:
        return ToolResult(
            success=False,
            error_message="PLAYWRIGHT_MCP_SERVER_URL environment variable is not set. Playwright tools are disabled."
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
        response = requests.post(server_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        # The response from playwright-mcp is the result itself
        return ToolResult(success=True, result=response.text)
    except requests.exceptions.Timeout:
        return ToolResult(success=False, error_message="The request to the Playwright server timed out (60 seconds).")
    except requests.exceptions.RequestException as e:
        return ToolResult(success=False, error_message=f"Failed to connect to the Playwright server: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred calling Playwright MCP: {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred: {e}")

# --- Individual Tools ---

def browser_navigate(url: str) -> ToolResult:
    """Navigates the browser to a specific URL."""
    if not url or not url.startswith(('http://', 'https://')):
        return ToolResult(success=False, error_message="Invalid URL. Must start with http:// or https://.")
    return _call_playwright_mcp("browser_navigate", {"url": url})

def browser_snapshot() -> ToolResult:
    """Captures a structured accessibility snapshot of the current page."""
    return _call_playwright_mcp("browser_snapshot", {})

def browser_click(ref: str, element: str) -> ToolResult:
    """Clicks on an element on the page, identified by a reference from a snapshot."""
    return _call_playwright_mcp("browser_click", {"ref": ref, "element": element})

def browser_type(ref: str, element: str, text: str) -> ToolResult:
    """Types text into an element on the page, identified by a reference from a snapshot."""
    return _call_playwright_mcp("browser_type", {"ref": ref, "element": element, "text": text})
