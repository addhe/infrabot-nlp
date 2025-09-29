import unittest
from unittest.mock import patch, MagicMock
import requests
from my_cli_agent.tools.tool_utils import call_mcp_server_helper
from my_cli_agent.models import ToolResult

class TestToolUtils(unittest.TestCase):

    @patch('os.getenv')
    @patch('requests.post')
    def test_call_mcp_server_helper_success(self, mock_post, mock_getenv):
        """Test a successful call to the MCP server helper."""
        # Arrange
        mock_getenv.return_value = 'http://fake-mcp-server.com'
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Success"}
        mock_post.return_value = mock_response

        # Act
        result = call_mcp_server_helper('test prompt', 'TEST_MCP_URL', 'test_tool')

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, "Success")
        mock_post.assert_called_once()

    @patch('os.getenv')
    def test_call_mcp_server_helper_no_env_var(self, mock_getenv):
        """Test the helper when the environment variable is not set."""
        # Arrange
        mock_getenv.return_value = None

        # Act
        result = call_mcp_server_helper('test prompt', 'TEST_MCP_URL', 'test_tool')

        # Assert
        self.assertFalse(result.success)
        self.assertIn("environment variable is not set", result.error_message)

    @patch('os.getenv')
    @patch('requests.post')
    def test_call_mcp_server_helper_timeout(self, mock_post, mock_getenv):
        """Test the helper when the request times out."""
        # Arrange
        mock_getenv.return_value = 'http://fake-mcp-server.com'
        mock_post.side_effect = requests.exceptions.Timeout

        # Act
        result = call_mcp_server_helper('test prompt', 'TEST_MCP_URL', 'test_tool')

        # Assert
        self.assertFalse(result.success)
        self.assertIn("timed out", result.error_message)

    @patch('os.getenv')
    @patch('requests.post')
    def test_call_mcp_server_helper_http_error(self, mock_post, mock_getenv):
        """Test the helper when the server returns an HTTP error."""
        # Arrange
        mock_getenv.return_value = 'http://fake-mcp-server.com'
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
        mock_post.return_value = mock_response

        # Act
        result = call_mcp_server_helper('test prompt', 'TEST_MCP_URL', 'test_tool')

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Failed to connect", result.error_message)

    @patch('os.getenv')
    @patch('requests.post')
    def test_call_mcp_server_helper_connection_error(self, mock_post, mock_getenv):
        """Test the helper when a connection error occurs."""
        # Arrange
        mock_getenv.return_value = 'http://fake-mcp-server.com'
        mock_post.side_effect = requests.exceptions.ConnectionError

        # Act
        result = call_mcp_server_helper('test prompt', 'TEST_MCP_URL', 'test_tool')

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Failed to connect", result.error_message)

    @patch('os.getenv')
    @patch('requests.post')
    def test_call_mcp_server_helper_unexpected_error(self, mock_post, mock_getenv):
        """Test the helper when an unexpected error occurs."""
        # Arrange
        mock_getenv.return_value = 'http://fake-mcp-server.com'
        mock_post.side_effect = Exception("Something went wrong")

        # Act
        result = call_mcp_server_helper('test prompt', 'TEST_MCP_URL', 'test_tool')

        # Assert
        self.assertFalse(result.success)
        self.assertIn("An unexpected error occurred", result.error_message)

if __name__ == '__main__':
    unittest.main()
