"""Unit tests for time tools functionality."""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from zoneinfo import ZoneInfo
from my_cli_agent.tools.time_tools import get_time_for_city, get_current_time

class TestTimeTools:
    @pytest.fixture
    def mock_datetime(self):
        with patch('my_cli_agent.tools.time_tools.datetime') as mock_dt:
            # Create a mock for the datetime object that will be returned by now()
            mock_now = MagicMock()
            mock_now.strftime.return_value = "12:00:00 +0800"
            
            # Configure the mock to return our mock_now when now() is called
            mock_dt.datetime.now.return_value = mock_now
            
            yield mock_dt

    def test_should_get_time_for_valid_city(self, mock_datetime):
        """Test getting time for a valid city."""
        # Arrange
        city = "singapore"
        
        # Act
        result = get_time_for_city(city)
        
        # Assert
        assert result.success is True
        assert isinstance(result.result, str)
        assert "singapore" in result.result.lower()
        # Verify that the result contains a time-like string (HH:MM:SS)
        assert ":" in result.result

    def test_should_handle_invalid_city(self):
        """Test handling invalid city names."""
        # Arrange
        city = "NonExistentCity"
        
        # Act
        result = get_time_for_city(city)
        
        # Assert
        assert result.success is False
        assert "Invalid city" in result.result

    def test_should_handle_empty_city_name(self):
        """Test handling empty city name."""
        # Act
        result = get_time_for_city("")
        
        # Assert
        assert result.success is False
        assert "City name cannot be empty" in result.result

    def test_get_current_time_with_city(self):
        """Test get_current_time with a specific city."""
        # Act
        result = get_current_time("singapore")
        
        # Assert
        assert result.success is True
        assert "singapore" in result.result.lower()

    def test_get_current_time_without_city_defaults_to_utc(self):
        """Test get_current_time without city defaults to UTC."""
        # Act
        result = get_current_time()
        
        # Assert
        assert result.success is True
        assert "UTC" in result.result

    def test_all_supported_cities(self):
        """Test that all supported cities work correctly."""
        supported_cities = [
            "singapore", "new york", "paris", "jakarta", 
            "tokyo", "london", "sydney", "utc"
        ]
        
        for city in supported_cities:
            result = get_time_for_city(city)
            assert result.success is True, f"Failed for city: {city}"
            assert city.lower() in result.result.lower(), f"City name not in result for: {city}"
            assert ":" in result.result, f"No time format found for: {city}"

    def test_case_insensitive_city_names(self):
        """Test that city names are case insensitive."""
        test_cases = [
            ("SINGAPORE", "singapore"),
            ("New York", "new york"),
            ("PARIS", "paris"),
            ("Tokyo", "tokyo")
        ]
        
        for input_city, expected_city in test_cases:
            result = get_time_for_city(input_city)
            assert result.success is True, f"Failed for city: {input_city}"
            assert expected_city in result.result.lower(), f"Expected city {expected_city} not found in result"
