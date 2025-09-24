import os
import unittest
from unittest.mock import patch, MagicMock
import requests
from my_cli_agent.tools.tool_utils import call_mcp_server_helper
from my_cli_agent.models import ToolResult

class TestToolUtils(unittest.TestCase):

    @patch('requests.post')
    @patch.dict(os.environ, {"MOCK_MCP_URL": "http://mock-server.com/"})
    def test_call_mcp_server_helper_success(self, mock_post):
        """Test the success case for the MCP server helper."""
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"response": "Success from MCP"}
        mock_post.return_value = mock_response

        # Act
        result = call_mcp_server_helper(
            prompt="test prompt",
            mcp_env_var="MOCK_MCP_URL",
            tool_name="mock_tool"
        )

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Success from MCP")
        mock_post.assert_called_once_with(
            "http://mock-server.com/",
            json={"prompt": "test prompt"},
            headers={"Content-Type": "application/json"},
            timeout=180
        )

    def test_call_mcp_server_helper_no_env_var(self):
        """Test the helper when the environment variable is not set."""
        # Arrange
        # Ensure the env var is not set
        if "MOCK_MCP_URL" in os.environ:
            del os.environ["MOCK_MCP_URL"]

        # Act
        result = call_mcp_server_helper(
            prompt="test prompt",
            mcp_env_var="MOCK_MCP_URL",
            tool_name="mock_tool"
        )

        # Assert
        self.assertFalse(result.success)
        self.assertIn("MOCK_MCP_URL environment variable is not set", result.error_message)

    @patch('requests.post', side_effect=requests.exceptions.Timeout)
    @patch.dict(os.environ, {"MOCK_MCP_URL": "http://mock-server.com/"})
    def test_call_mcp_server_helper_timeout(self, mock_post):
        """Test the helper's timeout exception handling."""
        # Act
        result = call_mcp_server_helper(
            prompt="test prompt",
            mcp_env_var="MOCK_MCP_URL",
            tool_name="mock_tool"
        )

        # Assert
        self.assertFalse(result.success)
        self.assertIn("timed out (180 seconds)", result.error_message)

    @patch('requests.post', side_effect=requests.exceptions.RequestException("Connection failed"))
    @patch.dict(os.environ, {"MOCK_MCP_URL": "http://mock-server.com/"})
    def test_call_mcp_server_helper_request_exception(self, mock_post):
        """Test the helper's request exception handling."""
        # Act
        result = call_mcp_server_helper(
            prompt="test prompt",
            mcp_env_var="MOCK_MCP_URL",
            tool_name="mock_tool"
        )

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Failed to connect", result.error_message)

    @patch('requests.post', side_effect=Exception("Unexpected error"))
    @patch.dict(os.environ, {"MOCK_MCP_URL": "http://mock-server.com/"})
    def test_call_mcp_server_helper_generic_exception(self, mock_post):
        """Test the helper's generic exception handling."""
        # Act
        result = call_mcp_server_helper(
            prompt="test prompt",
            mcp_env_var="MOCK_MCP_URL",
            tool_name="mock_tool"
        )

        # Assert
        self.assertFalse(result.success)
        self.assertIn("An unexpected error occurred", result.error_message)
