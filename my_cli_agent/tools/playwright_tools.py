import os
import logging
import requests
from my_cli_agent.models import ToolResult
from typing import Dict, Any

def _call_proxy(endpoint: str, json_payload: Dict[str, Any] = None) -> ToolResult:
    """Helper function to send a command to the Playwright Proxy service."""
    proxy_url = os.getenv("PLAYWRIGHT_PROXY_URL")
    if not proxy_url:
        return ToolResult(
            success=False,
            error_message="PLAYWRIGHT_PROXY_URL environment variable is not set. Playwright tools are disabled."
        )

    full_url = f"{proxy_url}/{endpoint}"
    
    try:
        if json_payload:
            response = requests.post(full_url, json=json_payload, timeout=60)
        else:
            response = requests.post(full_url, timeout=60)
            
        response.raise_for_status()
        # Assuming the proxy returns a JSON response that can be converted to a string
        return ToolResult(success=True, result=str(response.json()))
    except requests.exceptions.Timeout:
        return ToolResult(success=False, error_message="The request to the Playwright Proxy timed out (60 seconds).")
    except requests.exceptions.RequestException as e:
        return ToolResult(success=False, error_message=f"Failed to connect to the Playwright Proxy: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred calling Playwright Proxy: {e}", exc_info=True)
        return ToolResult(success=False, error_message=f"An unexpected error occurred: {e}")

# --- Individual Tools ---

def browser_initialize() -> ToolResult:
    """Initializes a new browser session via the stateful proxy."""
    return _call_proxy("initialize")

def browser_navigate(url: str) -> ToolResult:
    """Navigates the browser to a specific URL via the proxy."""
    if not url or not url.startswith(('http://', 'https://')):
        return ToolResult(success=False, error_message="Invalid URL. Must start with http:// or https://.")
    return _call_proxy("navigate", {"url": url})

def browser_snapshot() -> ToolResult:
    """Captures a structured accessibility snapshot via the proxy."""
    return _call_proxy("snapshot")

def browser_click(ref: str, element: str) -> ToolResult:
    """Clicks on an element on the page via the proxy."""
    return _call_proxy("click", {"ref": ref, "element": element})

def browser_type(ref: str, element: str, text: str) -> ToolResult:
    """Types text into an element on the page via the proxy."""
    return _call_proxy("type", {"ref": ref, "element": element, "text": text})
