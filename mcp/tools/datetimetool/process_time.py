import datetime

def get_current_time():
    """
    Returns the current time in HH:MM:SS format.
    
    Returns:
        str: Current time in HH:MM:SS format (e.g., "14:30:45")
    
    Usage:
        - "What time is it now?"
        - "Current time"
    """
    return datetime.datetime.now().strftime("%H:%M:%S")

def get_time_with_offset(offset: int, unit: str, base_datetime_str: str = None):
    """
    Calculates a new time by applying an offset to a given datetime or the current datetime.
    Returns only time (HH:MM:SS) if on the same day, or full datetime if on a different day.
    
    Args:
        offset (int): Number of units to add/subtract (positive for future, negative for past)
        unit (str): Time unit - 'seconds', 'minutes', or 'hours'
        base_datetime_str (str, optional): Base datetime in DD-MM-YYYY HH:MM:SS format. Uses current time if None.
    
    Returns:
        str: Time in HH:MM:SS format (same day) or DD-MM-YYYY HH:MM:SS format (different day), or error message
    
    Usage:
        - "Time 30 seconds from now" -> get_time_with_offset(30, 'seconds')
        - "Time 2 hours ago" -> get_time_with_offset(-2, 'hours')
        - "Time 90 minutes after 01-10-2025 10:00:00" -> get_time_with_offset(90, 'minutes', '01-10-2025 10:00:00')
    """
    try:
        if base_datetime_str:
            base_dt = datetime.datetime.strptime(base_datetime_str, "%d-%m-%Y %H:%M:%S")
        else:
            base_dt = datetime.datetime.now()
    except (ValueError, TypeError):
        return "Invalid base_datetime_str format. Please use 'DD-MM-YYYY HH:MM:SS'."

    if unit not in ['seconds', 'minutes', 'hours']:
        return f"Invalid unit '{unit}'. Please use 'seconds', 'minutes', or 'hours'."

    delta = datetime.timedelta(**{unit: offset})
    new_dt = base_dt + delta
    
    # Check if the new datetime is on the same date as the base datetime
    if new_dt.date() == base_dt.date():
        # Same day: return only time
        return new_dt.strftime("%H:%M:%S")
    else:
        # Different day: return full datetime
        return new_dt.strftime("%d-%m-%Y %H:%M:%S")

def get_time_range_for_day_part(part_of_day: str, base_date_str: str = None):
    """
    Returns a start and end time for a part of the day (morning, afternoon, evening).
    
    Args:
        part_of_day (str): Part of day - 'morning', 'afternoon', or 'evening'
        base_date_str (str, optional): Base date in DD-MM-YYYY format. Uses current date if None.
    
    Returns:
        dict: Dictionary with 'start_time' and 'end_time' keys in DD-MM-YYYY HH:MM:SS format
              Morning: 00:00:00-11:59:59, Afternoon: 12:00:00-17:59:59, Evening: 18:00:00-23:59:59
    
    Usage:
        - "Time range for this morning" -> get_time_range_for_day_part('morning')
        - "Time range for yesterday afternoon" -> get_time_range_for_day_part('afternoon', '17-07-2025')
        - "Time range for tomorrow evening" -> get_time_range_for_day_part('evening', '19-07-2025')
    """
    try:
        base_date = datetime.datetime.strptime(base_date_str, "%d-%m-%Y").date() if base_date_str else datetime.date.today()
    except (ValueError, TypeError):
        return "Invalid date format. Please use DD-MM-YYYY."

    part_of_day = part_of_day.lower()
    time_windows = {
        'morning': ('00:00:00', '11:59:59'),
        'afternoon': ('12:00:00', '17:59:59'),
        'evening': ('18:00:00', '23:59:59'),
    }

    if part_of_day not in time_windows:
        return f"Invalid part_of_day. Use 'morning', 'afternoon', or 'evening'."

    start_time_str, end_time_str = time_windows[part_of_day]
    date_str = base_date.strftime('%d-%m-%Y')

    return {
        "start_time": f"{date_str} {start_time_str}",
        "end_time": f"{date_str} {end_time_str}"
    }

def _get_date_with_offset_for_testing(offset: int, unit: str):
    """Internal helper for generating dates for test examples."""
    # This is a simplified version for demonstration within this script.
    # In a real MCP server, this would be a call to the process_date tool.
    from dateutil.relativedelta import relativedelta
    today = datetime.date.today()
    delta = relativedelta(**{unit: offset})
    return (today + delta).strftime("%d-%m-%Y")

if __name__ == '__main__':
    print("--- Time Tool Examples (20 Test Cases) ---")
    
    # Basic current time and simple offsets
    print(f"1. Current time: {get_current_time()}")
    print(f"2. Time in 30 seconds: {get_time_with_offset(30, 'seconds')}")
    print(f"3. Time 45 minutes ago: {get_time_with_offset(-45, 'minutes')}")
    print(f"4. Time in 3 hours: {get_time_with_offset(3, 'hours')}")
    print(f"5. Time 24 hours ago (yesterday this time): {get_time_with_offset(-24, 'hours')}")
    
    # Time ranges for different parts of today
    print(f"6. Time range for this morning: {get_time_range_for_day_part('morning')}")
    print(f"7. Time range for this afternoon: {get_time_range_for_day_part('afternoon')}")
    print(f"8. Time range for this evening: {get_time_range_for_day_part('evening')}")
    
    # Time ranges for other days
    tomorrow_date = _get_date_with_offset_for_testing(1, 'days')
    print(f"9. Time range for tomorrow morning: {get_time_range_for_day_part('morning', base_date_str=tomorrow_date)}")
    yesterday_date = _get_date_with_offset_for_testing(-1, 'days')
    print(f"10. Time range for yesterday afternoon: {get_time_range_for_day_part('afternoon', base_date_str=yesterday_date)}")
    print(f"11. Time range for yesterday evening: {get_time_range_for_day_part('evening', base_date_str=yesterday_date)}")
    
    # Time calculations from specific datetime strings
    base_dt_str = '01-10-2025 10:00:00'
    print(f"12. Time 90 mins from {base_dt_str}: {get_time_with_offset(90, 'minutes', base_datetime_str=base_dt_str)}")
    print(f"13. Time 2 hours before {base_dt_str}: {get_time_with_offset(-2, 'hours', base_datetime_str=base_dt_str)}")
    
    # More time offset examples
    print(f"14. Time 10 seconds ago: {get_time_with_offset(-10, 'seconds')}")
    print(f"15. Time 180 minutes ago: {get_time_with_offset(-180, 'minutes')}")
    print(f"16. Time in 4 hours (from now): {get_time_with_offset(4, 'hours')}")
    print(f"17. Time 5 minutes from now: {get_time_with_offset(5, 'minutes')}")
    print(f"18. Time 12 hours ago: {get_time_with_offset(-12, 'hours')}")
    
    # Chaining examples
    yesterday_afternoon = get_time_range_for_day_part('afternoon', base_date_str=yesterday_date)
    print(f"19. 30 mins into yesterday afternoon: {get_time_with_offset(30, 'minutes', base_datetime_str=yesterday_afternoon['start_time'])}")
    print(f"20. 1 hour before yesterday evening starts: {get_time_with_offset(-1, 'hours', base_datetime_str=get_time_range_for_day_part('evening', base_date_str=yesterday_date)['start_time'])}")
