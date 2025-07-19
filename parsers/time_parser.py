import re
from datetime import datetime, timedelta
from typing import Dict, Optional

def parse_time(query: str) -> Dict[str, Optional[any]]:
    """
    Parses the query string to extract time and time range information.
    """
    time_details = {"is_range": False, "time": None, "time_range": None}
    
    time_pattern_match = re.search(r'last\s+(\d+)\s+(day|hour|week|month|minute)s?', query)
    if time_pattern_match:
        time_quantity = int(time_pattern_match.group(1))
        time_unit = time_pattern_match.group(2)

        if time_unit in ["day", "week", "month"]:
            time_details["is_range"] = True
            current_date = datetime.now()
            if time_unit == "day":
                time_delta = timedelta(days=time_quantity)
            elif time_unit == "week":
                time_delta = timedelta(weeks=time_quantity)
            elif time_unit == "month":
                time_delta = timedelta(days=time_quantity * 30)
            
            calculated_start_date = current_date - time_delta
            time_details["time_range"] = {
                "start_date": calculated_start_date.strftime("%d-%m-%Y"),
                "end_date": current_date.strftime("%d-%m-%Y"),
            }
        elif time_unit in ["hour", "minute"]:
            current_date = datetime.now()
            time_details["time"] = current_date.strftime("%d-%m-%Y")
            
    return time_details
