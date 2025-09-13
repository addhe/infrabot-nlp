import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from typing import Dict
from my_cli_agent.models import ToolResult

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

def get_current_time(city: str = "UTC") -> ToolResult:
    """
    Gets the current time for a specified city.

    Args:
        city: The name of the city. Defaults to "UTC".

    Returns:
        A ToolResult object with the current time or an error message.
    """
    if not city:
        city = "UTC" # Default to UTC if city is an empty string

    city_lower = city.lower()
    tz_identifier = TIMEZONE_MAP.get(city_lower)

    if not tz_identifier:
        available_cities = ", ".join(sorted(TIMEZONE_MAP.keys()))
        return ToolResult(
            success=False,
            error_message=f"Unknown city: '{city}'. Available cities are: {available_cities}."
        )

    try:
        now = datetime.datetime.now(ZoneInfo(tz_identifier))
        formatted_time = now.strftime("%A, %Y-%m-%d %H:%M:%S %Z")
        return ToolResult(
            success=True,
            result=f"The current time in {city.title()} is {formatted_time}."
        )
    except ZoneInfoNotFoundError:
        return ToolResult(
            success=False,
            error_message=f"Timezone data not found for '{tz_identifier}'. The server environment may be misconfigured."
        )
    except Exception as e:
        return ToolResult(
            success=False,
            error_message=f"An unexpected error occurred while getting the time for '{city}': {e}"
        )
