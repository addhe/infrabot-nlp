import unittest
from unittest.mock import patch, MagicMock
from my_cli_agent.tools.markdown_tools import convert_file_to_markdown, HAS_MARKITDOWN
from my_cli_agent.models import ToolResult

# Mock the result object that the real MarkItDown library would return
class MockConversionResult:
    def __init__(self, text_content):
        self.text_content = text_content

@unittest.skipIf(not HAS_MARKITDOWN, "markitdown library not installed, skipping tests")
class TestMarkdownTools(unittest.TestCase):

    @patch('my_cli_agent.tools.markdown_tools.md_converter')
    def test_convert_file_success(self, mock_converter):
        """Test a successful file conversion."""
        # Arrange
        file_path = "document.pdf"
        mock_converter.convert.return_value = MockConversionResult("# My Document\nContent here.")
        
        # Act
        result = convert_file_to_markdown(file_path)

        # Assert
        self.assertTrue(result.success)
        self.assertEqual(result.result, "# My Document\nContent here.")
        mock_converter.convert.assert_called_once_with(file_path)

    @patch('my_cli_agent.tools.markdown_tools.md_converter')
    def test_convert_file_not_found(self, mock_converter):
        """Test when the file to be converted does not exist."""
        # Arrange
        file_path = "non_existent.docx"
        mock_converter.convert.side_effect = FileNotFoundError(f"File not found: {file_path}")

        # Act
        result = convert_file_to_markdown(file_path)

        # Assert
        self.assertFalse(result.success)
        self.assertIn("The file was not found", result.error_message)
        self.assertIn(file_path, result.error_message)

    @patch('my_cli_agent.tools.markdown_tools.md_converter')
    def test_convert_empty_content(self, mock_converter):
        """Test when conversion results in empty content."""
        # Arrange
        file_path = "empty.pdf"
        mock_converter.convert.return_value = MockConversionResult("")

        # Act
        result = convert_file_to_markdown(file_path)

        # Assert
        self.assertFalse(result.success)
        self.assertIn("resulted in empty content", result.error_message)

    def test_invalid_file_path(self):
        """Test providing an invalid or empty file path."""
        result_none = convert_file_to_markdown(None)
        self.assertFalse(result_none.success)
        self.assertEqual(result_none.error_message, "File path must be a non-empty string.")

        result_empty = convert_file_to_markdown("")
        self.assertFalse(result_empty.success)
        self.assertEqual(result_empty.error_message, "File path must be a non-empty string.")

if __name__ == '__main__':
    unittest.main()
