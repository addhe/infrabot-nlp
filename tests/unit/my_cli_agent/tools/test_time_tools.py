import unittest
from my_cli_agent.tools.time_tools import get_current_time
from my_cli_agent.models import ToolResult

class TestTimeTools(unittest.TestCase):

    def test_get_current_time_valid_city(self):
        """Test getting time for a valid, supported city."""
        result = get_current_time("jakarta")
        self.assertIsInstance(result, ToolResult)
        self.assertTrue(result.success)
        self.assertIn("The current time in Jakarta is", result.result)
        self.assertIsNone(result.error_message)

    def test_get_current_time_case_insensitive(self):
        """Test that city names are handled case-insensitively."""
        result = get_current_time("LoNdOn")
        self.assertTrue(result.success)
        self.assertIn("The current time in London is", result.result)

    def test_get_current_time_invalid_city(self):
        """Test getting time for an invalid or unsupported city."""
        result = get_current_time("atlantis")
        self.assertIsInstance(result, ToolResult)
        self.assertFalse(result.success)
        self.assertIsNone(result.result)
        self.assertIn("Unknown city: 'atlantis'", result.error_message)
        self.assertIn("Available cities are:", result.error_message)

    def test_get_current_time_default_utc(self):
        """Test that calling with no city defaults to UTC."""
        result = get_current_time()
        self.assertTrue(result.success)
        self.assertIn("The current time in Utc is", result.result)

    def test_get_current_time_empty_string_defaults_utc(self):
        """Test that calling with an empty string defaults to UTC."""
        result = get_current_time("")
        self.assertTrue(result.success)
        self.assertIn("The current time in Utc is", result.result)

if __name__ == '__main__':
    unittest.main()