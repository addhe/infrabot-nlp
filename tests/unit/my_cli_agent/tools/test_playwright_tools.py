import os
import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.tools.playwright_tools import (
    _call_proxy,
    browser_navigate,
    browser_snapshot,
    browser_click,
    browser_type
)
from my_cli_agent.models import ToolResult
import requests

class TestPlaywrightTools(unittest.TestCase):

    @patch.dict(os.environ, {"PLAYWRIGHT_PROXY_URL": "http://mock-playwright-server"})
    @patch('requests.post')
    def test_call_proxy_success(self, mock_post):
        """Test the internal helper function for a successful call."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_response

        # Act
        result = _call_proxy("test_endpoint", {"param": "value"})

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, "{'status': 'ok'}")
        mock_post.assert_called_once_with(
            "http://mock-playwright-server/test_endpoint",
            json={"param": "value"},
            timeout=60
        )

    def test_url_not_set(self):
        """Test that tools fail gracefully when the URL is not set."""
        if "PLAYWRIGHT_PROXY_URL" in os.environ:
            del os.environ["PLAYWRIGHT_PROXY_URL"]
        
        result = browser_navigate("https://example.com")
        self.assertFalse(result.success)
        self.assertIn("PLAYWRIGHT_PROXY_URL environment variable is not set", result.error_message)

    @patch('my_cli_agent.tools.playwright_tools._call_proxy')
    def test_browser_navigate(self, mock_call):
        """Test the browser_navigate tool function."""
        browser_navigate("https://google.com")
        mock_call.assert_called_once_with("navigate", {"url": "https://google.com"})

    def test_browser_navigate_invalid_url(self):
        """Test browser_navigate with an invalid URL."""
        result = browser_navigate("not-a-url")
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "Invalid URL. Must start with http:// or https://.")

    @patch('my_cli_agent.tools.playwright_tools._call_proxy')
    def test_browser_snapshot(self, mock_call):
        """Test the browser_snapshot tool function."""
        browser_snapshot()
        mock_call.assert_called_once_with("snapshot")

    @patch('my_cli_agent.tools.playwright_tools._call_proxy')
    def test_browser_click(self, mock_call):
        """Test the browser_click tool function."""
        browser_click(ref="ref123", element="Login Button")
        mock_call.assert_called_once_with("click", {"ref": "ref123", "element": "Login Button"})

    @patch('my_cli_agent.tools.playwright_tools._call_proxy')
    def test_browser_type(self, mock_call):
        """Test the browser_type tool function."""
        browser_type(ref="ref456", element="Username Input", text="admin")
        mock_call.assert_called_once_with("type", {"ref": "ref456", "element": "Username Input", "text": "admin"})

if __name__ == '__main__':
    unittest.main()
