"""Simplified tests for time_tools module."""
import pytest
from adk_cli_agent.tools.time_tools import get_current_time

class TestTimeToolsSimple:
    """Simplified test cases for time_tools module."""

    def test_get_current_time_supported_city(self):
        """Test that supported cities return a success status."""
        # Test with different capitalizations
        for city in ["New York", "PARIS", "london", "tOkYo"]:
            result = get_current_time(city)
            assert result["status"] == "success"
            assert f"The current time in {city}" in result["report"]

    def test_get_current_time_unsupported_city(self):
        """Test that unsupported cities return an error status."""
        result = get_current_time("Nonexistent City")
        assert result["status"] == "error"
        assert "is not supported" in result["error_message"]
        
        # Verify all supported cities are listed in the error message
        supported_cities = ["new york", "paris", "jakarta", "tokyo", "london", "sydney"]
        for city in supported_cities:
            assert city in result["error_message"].lower()
