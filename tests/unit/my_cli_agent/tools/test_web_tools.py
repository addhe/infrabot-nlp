import unittest
from unittest.mock import patch, MagicMock
import requests
from my_cli_agent.tools.web_tools import view_website
from my_cli_agent.models import ToolResult

class TestWebTools(unittest.TestCase):

    @patch('requests.get')
    def test_view_website_success(self, mock_get):
        """Test a successful website scrape."""
        # Arrange
        html_content = "<html><head><title>Test Page</title></head><body><p>Hello World</p></body></html>"
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = html_content
        mock_get.return_value = mock_response

        # Act
        result = view_website("https://example.com")

        # Assert
        self.assertTrue(result.success)
        self.assertIn("Hello World", result.result)
        self.assertIn("Test Page", result.result)
        mock_get.assert_called_once_with(
            "https://example.com",
            headers=unittest.mock.ANY,
            timeout=30
        )

    def test_view_website_invalid_url(self):
        """Test providing an invalid URL."""
        result = view_website("not-a-valid-url")
        self.assertFalse(result.success)
        self.assertIn("Invalid URL provided", result.error_message)

    @patch('requests.get', side_effect=requests.exceptions.Timeout)
    def test_view_website_timeout(self, mock_get):
        """Test a timeout during the request."""
        result = view_website("https://example.com")
        self.assertFalse(result.success)
        self.assertIn("The request to the URL timed out", result.error_message)

    @patch('requests.get', side_effect=requests.exceptions.RequestException("Connection Error"))
    def test_view_website_request_exception(self, mock_get):
        """Test a generic request exception."""
        result = view_website("https://example.com")
        self.assertFalse(result.success)
        self.assertIn("Failed to fetch the URL", result.error_message)

    @patch('requests.get')
    def test_view_website_no_text_content(self, mock_get):
        """Test a page that returns no text content after parsing."""
        # Arrange
        html_content = "<html><body><script>var x=1;</script></body></html>"
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = html_content
        mock_get.return_value = mock_response

        # Act
        result = view_website("https://example.com")

        # Assert
        self.assertFalse(result.success)
        self.assertIn("Could not extract any text content", result.error_message)

if __name__ == '__main__':
    unittest.main()
