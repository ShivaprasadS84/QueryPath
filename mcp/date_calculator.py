import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict
import calendar

def get_current_date() -> str:
    """Get current date in YYYY-MM-DD format"""
    return datetime.date.today().strftime("%Y-%m-%d")

def parse_reference_point(reference: str, offset_value: int, offset_unit: str) -> datetime.date:
    """
    Parse a reference point with offset to get actual date
    
    Args:
        reference: 'today', 'start_of_week', 'start_of_month', 'start_of_year', 'specific_month', 'specific_weekday', 'specific_day_of_month'
        offset_value: numeric offset (can be negative)
        offset_unit: 'days', 'weeks', 'months', 'years', 'month_name', 'weekday_name', 'day_number'
    
    Returns:
        datetime.date object
    """
    today = datetime.date.today()
    
    if reference == "today":
        base_date = today
        # Apply offset directly for simple cases
        if offset_unit == "days":
            return base_date + datetime.timedelta(days=offset_value)
        elif offset_unit == "weeks":
            # For "2 weeks ago", calculate exactly 14 days
            return base_date + datetime.timedelta(days=offset_value * 7)
        elif offset_unit == "months":
            # For "1 month ago", use same day in previous month
            return base_date + relativedelta(months=offset_value)
        elif offset_unit == "years":
            return base_date + relativedelta(years=offset_value)
            
    elif reference == "start_of_week":
        # Monday is start of week
        days_since_monday = today.weekday()
        base_date = today - datetime.timedelta(days=days_since_monday)
        # Apply week offset
        if offset_unit == "weeks":
            return base_date + datetime.timedelta(weeks=offset_value)
        elif offset_unit == "this":
            # For "this week", return start of current week
            return base_date
            
    elif reference == "start_of_month":
        base_date = today.replace(day=1)
        # Apply month offset
        if offset_unit == "months":
            return base_date + relativedelta(months=offset_value)
            
    elif reference == "start_of_year":
        base_date = today.replace(month=1, day=1)
        if offset_unit == "years":
            return base_date + relativedelta(years=offset_value)
            
    elif reference == "specific_month":
        # offset_unit contains month name, offset_value contains year offset
        month_names = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
            'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
            'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }
        month_num = month_names.get(offset_unit.lower(), today.month)
        year = today.year + offset_value
        base_date = datetime.date(year, month_num, 1)
        
    elif reference == "specific_weekday":
        # offset_unit contains weekday name, offset_value is direction (-1 for last, 1 for next)
        weekday_names = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_weekday = weekday_names.get(offset_unit.lower(), 0)
        current_weekday = today.weekday()
        
        if offset_value < 0:  # last occurrence
            days_back = (current_weekday - target_weekday) % 7
            if days_back == 0:
                days_back = 7  # If today is the target weekday, go back to last week
            base_date = today - datetime.timedelta(days=days_back)
        else:  # next occurrence
            days_forward = (target_weekday - current_weekday) % 7
            if days_forward == 0:
                days_forward = 7  # If today is the target weekday, go to next week
            base_date = today + datetime.timedelta(days=days_forward)
            
    elif reference == "specific_day_of_month":
        # offset_unit contains day number, offset_value is month offset (0=this month, -1=last month)
        try:
            day_number = int(offset_unit)
            target_month = today.replace(day=1) + relativedelta(months=offset_value)
            # Ensure the day exists in the target month
            max_day = calendar.monthrange(target_month.year, target_month.month)[1]
            if day_number > max_day:
                day_number = max_day
            base_date = target_month.replace(day=day_number)
        except (ValueError, TypeError):
            base_date = today
    else:
        base_date = today
    
    return base_date

def get_single_date(reference_point: str, offset_value: int, offset_unit: str) -> str:
    """
    Get a single date based on reference point and offset
    
    Returns:
        Date string in YYYY-MM-DD format
    """
    try:
        result_date = parse_reference_point(reference_point, offset_value, offset_unit)
        return result_date.strftime("%Y-%m-%d")
    except Exception as e:
        return f"Error: {str(e)}"

def get_week_range(week_offset: int = 0) -> Dict[str, str]:
    """
    Get a week range (Monday to Sunday)
    
    Args:
        week_offset: Week offset from current week (0 = this week, -1 = last week)
    
    Returns:
        Dictionary with 'start_date' and 'end_date' keys
    """
    try:
        today = datetime.date.today()
        # Monday is start of week
        days_since_monday = today.weekday()
        start_of_current_week = today - datetime.timedelta(days=days_since_monday)
        
        # Apply week offset
        start_date = start_of_current_week + datetime.timedelta(weeks=week_offset)
        end_date = start_date + datetime.timedelta(days=6)  # Sunday
        
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

def get_date_range(
    start_reference: str, start_offset_value: int, start_offset_unit: str,
    end_reference: str, end_offset_value: int, end_offset_unit: str
) -> Dict[str, str]:
    """
    Get a date range with start and end dates
    
    Returns:
        Dictionary with 'start_date' and 'end_date' keys
    """
    try:
        start_date = parse_reference_point(start_reference, start_offset_value, start_offset_unit)
        end_date = parse_reference_point(end_reference, end_offset_value, end_offset_unit)
        
        # For month/week ranges, adjust to proper boundaries
        if start_reference == "start_of_month" and end_reference == "start_of_month":
            # Full month range
            end_date = end_date + relativedelta(months=1) - datetime.timedelta(days=1)
        elif start_reference == "start_of_week" and end_reference == "start_of_week":
            # Full week range (Monday to Sunday)
            end_date = end_date + datetime.timedelta(days=6)
        elif start_reference == "specific_month" and end_reference == "specific_month":
            # Handle specific month ranges like "march and april" or "jan to march"
            if start_offset_unit != end_offset_unit:  # Different months
                # Get last day of end month
                end_month_year = end_date.year
                end_month_num = end_date.month
                last_day = calendar.monthrange(end_month_year, end_month_num)[1]
                end_date = end_date.replace(day=last_day)
        
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

def get_month_range(month_name: str, year_offset: int = 0) -> Dict[str, str]:
    """
    Get full month range for a specific month
    
    Args:
        month_name: Name of the month (e.g., 'february', 'feb')
        year_offset: Year offset from current year (0 = this year, -1 = last year)
    
    Returns:
        Dictionary with 'start_date' and 'end_date' keys
    """
    try:
        month_names = {
            'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3,
            'april': 4, 'apr': 4, 'may': 5, 'june': 6, 'jun': 6, 'july': 7, 'jul': 7,
            'august': 8, 'aug': 8, 'september': 9, 'sep': 9, 'october': 10, 'oct': 10,
            'november': 11, 'nov': 11, 'december': 12, 'dec': 12
        }
        
        month_num = month_names.get(month_name.lower())
        if not month_num:
            return {"error": f"Invalid month name: {month_name}"}
        
        year = datetime.date.today().year + year_offset
        start_date = datetime.date(year, month_num, 1)
        
        # Get last day of month
        last_day = calendar.monthrange(year, month_num)[1]
        end_date = datetime.date(year, month_num, last_day)
        
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
    except Exception as e:
        return {"error": f"Error: {str(e)}"}

# Test functions
if __name__ == "__main__":
    print("=== Date Calculator Tests ===")
    print(f"Current date: {get_current_date()}")
    print(f"Yesterday: {get_single_date('today', -1, 'days')}")
    print(f"Last week range: {get_date_range('start_of_week', -1, 'weeks', 'start_of_week', -1, 'weeks')}")
    print(f"February range: {get_month_range('february', 0)}")
    print(f"Last Thursday: {get_single_date('specific_weekday', -1, 'thursday')}")
    print(f"3rd of this month: {get_single_date('specific_day_of_month', 0, '3')}")
    print(f"15th of last month: {get_single_date('specific_day_of_month', -1, '15')}")
