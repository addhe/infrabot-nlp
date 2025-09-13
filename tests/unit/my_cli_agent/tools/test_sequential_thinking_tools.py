import os
import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.tools.sequential_thinking_tools import call_sequential_thinking_server
from my_cli_agent.models import ToolResult
import requests

class TestSequentialThinkingTools(unittest.TestCase):

    @patch.dict(os.environ, {"SEQ_THINKING_MCP_SERVER_URL": "http://mock-seq-server:8001"})
    @patch('requests.post')
    def test_call_server_success(self, mock_post):
        """Test a successful call to the sequential thinking server."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Step 1: Do this. Step 2: Do that."}
        mock_post.return_value = mock_response

        # Act
        result = call_sequential_thinking_server("how to bake a cake?")

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Step 1: Do this. Step 2: Do that.")
        mock_post.assert_called_once_with(
            "http://mock-seq-server:8001/",
            json={"prompt": "how to bake a cake?"},
            headers={"Content-Type": "application/json"},
            timeout=90
        )

    @patch.dict(os.environ, {"SEQ_THINKING_MCP_SERVER_URL": "http://mock-seq-server:8001"})
    @patch('requests.post')
    def test_call_server_http_error(self, mock_post):
        """Test a call that results in an HTTP error."""
        # Arrange
        mock_post.side_effect = requests.exceptions.HTTPError("503 Service Unavailable")

        # Act
        result = call_sequential_thinking_server("a failing prompt")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Failed to connect to the Sequential Thinking server", result.error_message)
        self.assertIn("503 Service Unavailable", result.error_message)

    @patch.dict(os.environ, {"SEQ_THINKING_MCP_SERVER_URL": "http://mock-seq-server:8001"})
    @patch('requests.post')
    def test_call_server_timeout(self, mock_post):
        """Test a call that times out."""
        # Arrange
        mock_post.side_effect = requests.exceptions.Timeout

        # Act
        result = call_sequential_thinking_server("a very long prompt")

        # Assert
        self.assertFalse(result.success)
        self.assertEqual(result.error_message, "The request to the Sequential Thinking server timed out (90 seconds).")

    def test_server_url_not_set(self):
        """Test when the SEQ_THINKING_MCP_SERVER_URL environment variable is not set."""
        # Arrange
        if "SEQ_THINKING_MCP_SERVER_URL" in os.environ:
            del os.environ["SEQ_THINKING_MCP_SERVER_URL"]

        # Act
        result = call_sequential_thinking_server("any prompt")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("SEQ_THINKING_MCP_SERVER_URL environment variable is not set", result.error_message)

if __name__ == '__main__':
    unittest.main()
