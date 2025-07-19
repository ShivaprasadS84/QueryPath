import datetime
from dateutil.relativedelta import relativedelta

def get_current_date():
    """
    Returns the current date in DD-MM-YYYY format.
    
    Returns:
        str: Current date in DD-MM-YYYY format (e.g., "18-07-2025")
    
    Usage:
        - "What is today's date?"
        - "Current date"
    """
    return datetime.date.today().strftime("%d-%m-%Y")

def get_date_with_offset(offset: int, unit: str, base_date_str: str = None):
    """
    Calculates a new date by applying an offset to a given date or the current date.
    
    Args:
        offset (int): Number of units to add/subtract (positive for future, negative for past)
        unit (str): Time unit - 'days', 'weeks', 'months', or 'years'
        base_date_str (str, optional): Base date in DD-MM-YYYY format. Uses current date if None.
    
    Returns:
        str: Calculated date in DD-MM-YYYY format or error message
    
    Usage:
        - "Date 5 days from now" -> get_date_with_offset(5, 'days')
        - "Date 3 weeks ago" -> get_date_with_offset(-3, 'weeks')
        - "Date 6 months after 01-01-2025" -> get_date_with_offset(6, 'months', '01-01-2025')
    """
    try:
        base_date = datetime.datetime.strptime(base_date_str, "%d-%m-%Y").date() if base_date_str else datetime.date.today()
    except (ValueError, TypeError):
        return "Invalid base_date_str format. Please use DD-MM-YYYY."

    if unit not in ['days', 'weeks', 'months', 'years']:
        return f"Invalid unit '{unit}'. Please use 'days', 'weeks', 'months', or 'years'."

    delta = relativedelta(**{unit: offset})
    new_date = base_date + delta
    return new_date.strftime("%d-%m-%Y")

def get_day_of_week(date_str: str = None):
    """
    Returns the day of the week for a given date or the current date.
    
    Args:
        date_str (str, optional): Date in DD-MM-YYYY format. Uses current date if None.
    
    Returns:
        str: Day of the week (e.g., "Monday", "Tuesday") or error message
    
    Usage:
        - "What day is today?" -> get_day_of_week()
        - "What day is 25-12-2025?" -> get_day_of_week('25-12-2025')
    """
    try:
        target_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date() if date_str else datetime.date.today()
        return target_date.strftime('%A')
    except ValueError:
        return "Invalid date format. Please use DD-MM-YYYY."

def get_date_of_weekday(weekday_name: str, direction: str, base_date_str: str = None):
    """
    Finds the date of the next or last occurrence of a specific weekday.
    
    Args:
        weekday_name (str): Name of the weekday ('Monday', 'Tuesday', etc.)
        direction (str): 'next' for future occurrence, 'last' for past occurrence
        base_date_str (str, optional): Base date in DD-MM-YYYY format. Uses current date if None.
    
    Returns:
        str: Date of the weekday in DD-MM-YYYY format or error message
    
    Usage:
        - "When is next Monday?" -> get_date_of_weekday('Monday', 'next')
        - "When was last Friday?" -> get_date_of_weekday('Friday', 'last')
    """
    days_of_week = [d.lower() for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']]
    weekday_name = weekday_name.lower()
    if weekday_name not in days_of_week:
        return f"Invalid weekday_name '{weekday_name}'."

    try:
        base_date = datetime.datetime.strptime(base_date_str, "%d-%m-%Y").date() if base_date_str else datetime.date.today()
    except (ValueError, TypeError):
        return "Invalid base_date_str format. Please use DD-MM-YYYY."

    target_weekday = days_of_week.index(weekday_name)
    base_weekday = base_date.weekday()

    if direction == 'last':
        day_diff = (base_weekday - target_weekday + 7) % 7
        if day_diff == 0:
            day_diff = 7
        new_date = base_date - datetime.timedelta(days=day_diff)
    elif direction == 'next':
        day_diff = (target_weekday - base_weekday + 7) % 7
        if day_diff == 0:
            day_diff = 7
        new_date = base_date + datetime.timedelta(days=day_diff)
    else:
        return "Invalid direction. Please use 'next' or 'last'."
    
    return new_date.strftime("%d-%m-%Y")

def get_start_of_period(period: str, base_date_str: str = None):
    """
    Returns the start date of a period (week, month, or year).
    
    Args:
        period (str): Period type - 'week', 'month', or 'year'
        base_date_str (str, optional): Base date in DD-MM-YYYY format. Uses current date if None.
    
    Returns:
        str: Start date of the period in DD-MM-YYYY format or error message
    
    Usage:
        - "Start of this week" -> get_start_of_period('week')
        - "Start of this month" -> get_start_of_period('month')
        - "Start of this year" -> get_start_of_period('year')
    """
    try:
        base_date = datetime.datetime.strptime(base_date_str, "%d-%m-%Y").date() if base_date_str else datetime.date.today()
    except (ValueError, TypeError):
        return "Invalid base_date_str format. Please use DD-MM-YYYY."

    if period == 'week':
        start_date = base_date - datetime.timedelta(days=base_date.weekday())
    elif period == 'month':
        start_date = base_date.replace(day=1)
    elif period == 'year':
        start_date = base_date.replace(month=1, day=1)
    else:
        return "Invalid period. Use 'week', 'month', or 'year'."
    return start_date.strftime("%d-%m-%Y")

def get_end_of_period(period: str, base_date_str: str = None):
    """
    Returns the end date of a period (week, month, or year).
    
    Args:
        period (str): Period type - 'week', 'month', or 'year'
        base_date_str (str, optional): Base date in DD-MM-YYYY format. Uses current date if None.
    
    Returns:
        str: End date of the period in DD-MM-YYYY format or error message
    
    Usage:
        - "End of this week" -> get_end_of_period('week')
        - "End of this month" -> get_end_of_period('month')
        - "End of this year" -> get_end_of_period('year')
    """
    try:
        base_date = datetime.datetime.strptime(base_date_str, "%d-%m-%Y").date() if base_date_str else datetime.date.today()
    except (ValueError, TypeError):
        return "Invalid base_date_str format. Please use DD-MM-YYYY."

    if period == 'week':
        end_date = base_date + datetime.timedelta(days=6 - base_date.weekday())
    elif period == 'month':
        next_month = base_date.replace(day=28) + datetime.timedelta(days=4) # Go to next month
        end_date = next_month - datetime.timedelta(days=next_month.day)
    elif period == 'year':
        end_date = base_date.replace(month=12, day=31)
    else:
        return "Invalid period. Use 'week', 'month', or 'year'."
    return end_date.strftime("%d-%m-%Y")

def get_date_range_for_week(offset: int = 0):
    """
    Gets the start and end dates for a week, with an offset from the current week.
    
    Args:
        offset (int): Week offset from current week (0=current, -1=last, 1=next)
    
    Returns:
        dict: Dictionary with 'start_date' and 'end_date' keys in DD-MM-YYYY format
              Week starts on Monday and ends on Sunday
    
    Usage:
        - "This week's date range" -> get_date_range_for_week(0)
        - "Last week's date range" -> get_date_range_for_week(-1)
        - "Next week's date range" -> get_date_range_for_week(1)
    """
    today = datetime.date.today()
    # Calculate the start of the current week (Monday)
    current_week_start = today - datetime.timedelta(days=today.weekday())
    # Apply the offset
    target_week_start = current_week_start + datetime.timedelta(weeks=offset)
    target_week_end = target_week_start + datetime.timedelta(days=6)
    
    return {
        "start_date": target_week_start.strftime("%d-%m-%Y"),
        "end_date": target_week_end.strftime("%d-%m-%Y")
    }

def get_date_range_for_quarter(offset: int = 0):
    """
    Gets the start and end dates for a quarter, with an offset from the current quarter.
    
    Args:
        offset (int): Quarter offset from current quarter (0=current, -1=last, 1=next)
    
    Returns:
        dict: Dictionary with 'start_date' and 'end_date' keys in DD-MM-YYYY format
              Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec
    
    Usage:
        - "This quarter's date range" -> get_date_range_for_quarter(0)
        - "Last quarter's date range" -> get_date_range_for_quarter(-1)
        - "Next quarter's date range" -> get_date_range_for_quarter(1)
    """
    today = datetime.date.today()
    current_quarter = (today.month - 1) // 3 + 1
    target_quarter_val = (today.year * 4) + current_quarter + offset
    
    target_year = (target_quarter_val -1) // 4
    target_quarter_num = (target_quarter_val -1) % 4 + 1

    start_month = 3 * target_quarter_num - 2
    end_month = 3 * target_quarter_num

    start_date = datetime.date(target_year, start_month, 1)
    end_date = datetime.date(target_year, end_month, 1).replace(day=1) + relativedelta(months=1, days=-1)

    return {
        "start_date": start_date.strftime("%d-%m-%Y"),
        "end_date": end_date.strftime("%d-%m-%Y")
    }

if __name__ == '__main__':
    print("--- Date Tool Examples (20 Test Cases) ---")
    
    # Basic current date and offsets
    print(f"1. Current date: {get_current_date()}")
    print(f"2. Date in 10 days: {get_date_with_offset(10, 'days')}")
    print(f"3. Date 3 weeks ago: {get_date_with_offset(-3, 'weeks')}")
    print(f"4. Date in 6 months: {get_date_with_offset(6, 'months')}")
    print(f"5. Date 2 years ago: {get_date_with_offset(-2, 'years')}")
    
    # Day of week queries
    print(f"6. Day of week for 25-12-2025: {get_day_of_week('25-12-2025')}")
    print(f"7. Today's day of the week: {get_day_of_week()}")
    print(f"8. Day of week for 01-01-2025: {get_day_of_week('01-01-2025')}")
    
    # Weekday finding
    print(f"9. Date of next Monday: {get_date_of_weekday('Monday', 'next')}")
    print(f"10. Date of last Friday: {get_date_of_weekday('Friday', 'last')}")
    print(f"11. Date of next Wednesday: {get_date_of_weekday('Wednesday', 'next')}")
    print(f"12. Date of last Sunday: {get_date_of_weekday('Sunday', 'last')}")
    
    # Period boundaries
    print(f"13. Start of this week: {get_start_of_period('week')}")
    print(f"14. End of this month: {get_end_of_period('month')}")
    print(f"15. Start of this year: {get_start_of_period('year')}")
    print(f"16. End of this week: {get_end_of_period('week')}")
    
    # Week ranges
    print(f"17. Date range for current week: {get_date_range_for_week(0)}")
    print(f"18. Date range for last week: {get_date_range_for_week(-1)}")
    print(f"19. Date range for next week: {get_date_range_for_week(1)}")
    
    # Chaining example
    next_tuesday = get_date_of_weekday('Tuesday', 'next')
    print(f"20. Date 1 month after next Tuesday ({next_tuesday}): {get_date_with_offset(1, 'months', base_date_str=next_tuesday)}")

