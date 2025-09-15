import os
import logging
from flask import Flask, request, jsonify
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# This session object will maintain the persistent connection to the actual Playwright MCP server.
# It handles cookies and keeps the connection alive.
mcp_session = requests.Session()
mcp_session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream"
})

# The URL of the real Playwright service, configured via environment variable.
PLAYWRIGHT_SERVICE_URL = os.environ.get("PLAYWRIGHT_SERVICE_URL")

def forward_request(method: str, params: dict) -> tuple[dict, int]:
    """Forwards a JSON-RPC request to the real Playwright service."""
    if not PLAYWRIGHT_SERVICE_URL:
        logging.error("PLAYWRIGHT_SERVICE_URL is not set!")
        return {"error": "Proxy is not configured"}, 500

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    
    try:
        response = mcp_session.post(f"{PLAYWRIGHT_SERVICE_URL}/mcp", json=payload, timeout=60)
        # Do NOT raise_for_status; we want to pass through upstream error codes/bodies for clarity
        try:
            body = response.json()
        except ValueError:
            body = {"error": response.text}
        return body, response.status_code
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to connect to Playwright service: {e}")
        # If the connection fails, try to reset the session for the next attempt.
        mcp_session.close()
        return {"error": f"Connection to Playwright service failed: {e}"}, 502
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
        return {"error": f"An unexpected error occurred: {e}"}, 500

@app.route('/initialize', methods=['POST'])
def initialize():
    """Initializes the browser session."""
    # Try the standard MCP initialize method name with basic params
    init_params = {
        "clientInfo": {"name": "infrabot-playwright-proxy", "version": "0.1.0"},
        "protocolVersion": "2024-11-05",
        "capabilities": {}
    }
    init_body, init_status = forward_request("initialize", init_params)
    # If initialize failed, return as-is
    if not (200 <= init_status < 300):
        return init_body, init_status
    # Complete handshake with 'initialized' notification (no params)
    _initialized_body, _initialized_status = forward_request("initialized", {})
    # We ignore errors on the notification, but log if needed
    if not (200 <= _initialized_status < 300):
        logging.warning(f"'initialized' notification returned status {_initialized_status}: {_initialized_body}")
    return init_body, init_status

@app.route('/navigate', methods=['POST'])
def navigate():
    """Navigates to a URL."""
    data = request.get_json()
    return forward_request("browser_navigate", {"url": data.get("url")})

@app.route('/snapshot', methods=['POST'])
def snapshot():
    """Takes a snapshot."""
    return forward_request("browser_snapshot", {})

@app.route('/click', methods=['POST'])
def click():
    """Clicks an element."""
    data = request.get_json()
    return forward_request("browser_click", {"ref": data.get("ref"), "element": data.get("element")})

@app.route('/type', methods=['POST'])
def type_text():
    """Types text into an element."""
    data = request.get_json()
    return forward_request("browser_type", {"ref": data.get("ref"), "element": data.get("element"), "text": data.get("text")})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
