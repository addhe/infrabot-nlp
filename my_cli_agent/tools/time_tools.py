import datetime
from zoneinfo import ZoneInfo
from typing import Dict
from .base import ToolResult

# Map of supported cities to their timezone identifiers
TIMEZONE_MAP: Dict[str, str] = {
    "singapore": "Asia/Singapore",
    "new york": "America/New_York",
    "paris": "Europe/Paris",
    "jakarta": "Asia/Jakarta",
    "tokyo": "Asia/Tokyo",
    "london": "Europe/London",
    "sydney": "Australia/Sydney",
    "utc": "UTC"
}

def get_current_time(city: str = "") -> ToolResult:
    """
    Get the current time for a city.
    
    Args:
        city: Name of the city to get time for. Defaults to UTC if not provided.
        
    Returns:
        ToolResult containing the current time or an error message.
    """
    return get_time_for_city(city if city else "UTC")

def get_time_for_city(city: str) -> ToolResult:
    """
    Returns the current time for a specified city.
    
    Args:
        city: Name of the city to get time for
        
    Returns:
        ToolResult containing the current time or an error message
    """
    if not city:
        return ToolResult(
            success=False,
            result="City name cannot be empty"
        )
    
    city_lower = city.lower()
    tz_identifier = TIMEZONE_MAP.get(city_lower)
    
    if not tz_identifier:
        available_cities = ", ".join(sorted(TIMEZONE_MAP.keys()))
        return ToolResult(
            success=False,
            result=f"Invalid city: {city}. Available cities: {available_cities}"
        )
    
    try:
        current_time = datetime.datetime.now(ZoneInfo(tz_identifier))
        formatted_time = current_time.strftime("%H:%M:%S %Z%z")
        return ToolResult(
            success=True,
            result=f"Current time in {city}: {formatted_time}"
        )
    except Exception as e:
        return ToolResult(
            success=False,
            result=f"Error getting time for {city}: {str(e)}"
        )