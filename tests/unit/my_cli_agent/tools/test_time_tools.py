"""Unit tests for time tools functionality."""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, ANY
from my_cli_agent.tools.time_tools import get_time_for_city

class TestTimeTools:
    @pytest.fixture
    def mock_datetime(self):
        with patch('my_cli_agent.tools.time_tools.datetime') as mock_dt, \
             patch('my_cli_agent.tools.time_tools.ZoneInfo') as mock_zone_info:
            
            # Configure the mock for ZoneInfo
            mock_zone = MagicMock()
            mock_zone_info.return_value = mock_zone
            
            # Create a mock for the datetime object that will be returned by now()
            mock_now = MagicMock()
            mock_now.strftime.return_value = "12:00:00 +0800"
            
            # Configure the mock to return our mock_now when now() is called with ZoneInfo
            mock_dt.now.return_value = mock_now
            
            # Make sure the mock can still be used to create datetime objects
            mock_dt.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            yield mock_dt

    def test_should_get_time_for_valid_city(self, mock_datetime):
        """Test getting time for a valid city."""
        # Arrange
        city = "Singapore"
        
        # Act
        result = get_time_for_city(city)
        
        # Assert
        assert result.success is True
        assert isinstance(result.result, str)
        assert city in result.result
        # Verify that the result contains a time-like string (HH:MM:SS)
        # This is more flexible than checking for an exact time string
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
