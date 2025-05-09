"""Time-related tools for ADK CLI Agent."""

def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.
    
    Args:
        city (str): The name of the city for which to retrieve the current time.
        
    Returns:
        dict: status and result or error message.
    """
    print(f"--- Tool: get_current_time called with city={city} ---")
    
    TIMEZONE_MAP = {
        "new york": "America/New_York",
        "paris": "Europe/Paris",
        "jakarta": "Asia/Jakarta",
        "tokyo": "Asia/Tokyo",
        "london": "Europe/London",
        "sydney": "Australia/Sydney"
    }

    import datetime
    from zoneinfo import ZoneInfo
    
    city_lower = city.lower()
    tz_identifier = TIMEZONE_MAP.get(city_lower)

    if tz_identifier:
        try:
            tz = ZoneInfo(tz_identifier)
            current_time = datetime.datetime.now(tz)
            time_str = current_time.strftime("%H:%M:%S %Z%z")
            return {
                "status": "success",
                "report": f"The current time in {city} is {time_str}"
            }
        except Exception as e:
            return {
                "status": "error",
                "error_message": f"Could not determine time for {city}: {e}"
            }
    else:
        return {
            "status": "error",
            "error_message": (f"Timezone for '{city}' is not supported. "
                             f"Supported cities: {', '.join(TIMEZONE_MAP.keys())}")
        }
