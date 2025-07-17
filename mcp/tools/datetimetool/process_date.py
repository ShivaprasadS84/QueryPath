import datetime
import re
from dateutil.relativedelta import relativedelta

# --- Constants for Parsing ---

UNIT_PATTERN = r'(d|day|w|wk|wks|week|mo|mos|month|y|yr|yrs|year)s?'
DIRECTION_PATTERN = r'(ago|from now|before|after|next|last|back|in)'
NUM_PATTERN = r'(a\s+couple\s+of|the|a|\d+)'
WEEKDAY_PATTERN = r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'

# Compiled regex for performance
REGEX_PATTERNS = [
    # Pattern 1: "next week", "last month"
    re.compile(rf'(next|last)\s+({WEEKDAY_PATTERN}|week|month|year)'),
    # Pattern 2: "3 months ago", "a week from now"
    re.compile(rf'{NUM_PATTERN}\s*{UNIT_PATTERN}\s*{DIRECTION_PATTERN}'),
    # Pattern 3: "after 5d", "in 2 weeks"
    re.compile(rf'{DIRECTION_PATTERN}\s*{NUM_PATTERN}\s*{UNIT_PATTERN}'),
]

# --- Helper Functions ---
def _is_numeric(s):
    """Checks if a string can be converted to a digit"""
    return s.isdigit()

def _parse_numeric_string(s):
    """Converts number words to digits"""
    return s.replace('a couple of', '2').replace('a', '1').replace('the', '1')

# --- Core Parsing Logic ---
def _parse_date_query(query):
    """Parses a natural language query to extract date information"""
    if not isinstance(query, str):
        return None

    lq = query.lower()

    # Tier 1: Check for special keywords first. This is more precise to avoid partial matches.
    if 'day after tomorrow' in lq: return (2, 'days', 'from now')
    if 'day before yesterday' in lq: return (2, 'days', 'ago')
    if 'tomorrow' in lq: return (1, 'days', 'from now')
    if 'yesterday' in lq: return (1, 'days', 'ago')
    if re.search(r'\bfortnight\b', lq):
        return (2, 'weeks', 'from now' if 'from now' in lq or 'in' in lq else 'ago')

    # Tier 2: Match against compiled regex patterns
    for i, pattern in enumerate(REGEX_PATTERNS):
        match = pattern.search(lq)
        if not match:
            continue

        if i == 0:  # "next week", "last month"
            return (1, match.group(2), match.group(1))
        
        num_str = _parse_numeric_string(match.group(1 if i == 1 else 2))
        if _is_numeric(num_str):
            if i == 1:  # "3 months ago"
                return (int(num_str), match.group(2), match.group(3))
            if i == 2:  # "after 5d"
                return (int(num_str), match.group(3), match.group(1))

    return None

# --- Main Calculation Function ---
def calculate_date(query):
    """Calculates a new date based on a natural language query from the current date"""
    parsed_query = _parse_date_query(query)
    if not parsed_query:
        return "Invalid query format. Please use a valid format."

    value, unit, direction = parsed_query
    today = datetime.date.today()

    # Normalize units for relativedelta
    norm_unit = unit.lower()
    final_unit = None
    if norm_unit.startswith('d'): final_unit = 'days'
    elif norm_unit.startswith('w'): final_unit = 'weeks'
    elif norm_unit.startswith('m'): final_unit = 'months'
    elif norm_unit.startswith('y'): final_unit = 'years'

    # Handle weekday logic
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if unit in days_of_week:
        target_weekday = days_of_week.index(unit)
        today_weekday = today.weekday()
        if direction == 'last':
            days_ahead = (target_weekday - today_weekday) - 7
        else:
            days_ahead = (target_weekday - today_weekday + 7) % 7
            if days_ahead == 0 and direction == 'next':
                days_ahead = 7
        new_date = today + datetime.timedelta(days=days_ahead)
    # Handle relativedelta logic for other units
    elif final_unit:
        delta = relativedelta(**{final_unit: value})
        new_date = today - delta if direction in ['ago', 'before', 'last', 'back'] else today + delta
    else:
        return "Invalid unit specified."

    return new_date.strftime("%Y-%m-%d")

# --- Example Usage ---
if __name__ == "__main__":
    print(f"Current date: {datetime.date.today().strftime('%Y-%m-%d')}")
    queries = [
        "What will the date be 2 years from now?",
        "What was the date 3 months ago?",
        "Show me the date after 2 wks.",
        "What was the date before 5d?",
        "After 1 yr what is the date?",
        "What is the date next week?",
        "What was the date last month?",
        "What is tomorrow's date?",
        "What was yesterday's date?",
        "Date day after tomorrow?",
        "Date on the day before yesterday?",
        "What is the date next Friday?",
        "What was the date last Monday?",
        "What is the date a couple of months from now?",
        "Before a couple of weeks, what was the date?",
        "1 day back, what was the date?",
        "Invalid query"
    ]

    for q in queries:
        print(f"Query: '{q}' -> Result: {calculate_date(q)}")
