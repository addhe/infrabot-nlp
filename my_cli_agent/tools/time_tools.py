import datetime
from zoneinfo import ZoneInfo
from typing import Any, Optional
from .base import ToolResult

def get_current_time(city: str) -> ToolResult:
    """Returns the current time in a specified city."""
    print(f"--- Tool: get_current_time called with city={city} ---")
    
    TIMEZONE_MAP = {
        "new york": "America/New_York",
        "paris": "Europe/Paris",
        "jakarta": "Asia/Jakarta",
        "tokyo": "Asia/Tokyo",
        "london": "Europe/London",
        "sydney": "Australia/Sydney"
    }

    city_lower = city.lower()
    tz_identifier = TIMEZONE_MAP.get(city_lower)

    if tz_identifier:
        try:
            tz = ZoneInfo(tz_identifier)
            current_time = datetime.datetime.now(tz)
            time_str = current_time.strftime("%H:%M:%S %Z%z")
            return ToolResult(
                success=True,
                result=time_str
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error_message=f"Could not determine time for {city}: {e}"
            )
    else:
        return ToolResult(
            success=False,
            error_message=f"Timezone for '{city}' is not supported. Supported cities: {', '.join(TIMEZONE_MAP.keys())}"
        )