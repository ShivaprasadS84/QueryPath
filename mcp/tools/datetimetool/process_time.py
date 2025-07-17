import datetime
import re

# --- Constants for Parsing ---
UNIT_PATTERN = r'(hour|hr|minute|min|second|sec)s?'
DIRECTION_PATTERN = r'(ago|from now|before|after|next|last|back|in)'
NUM_PATTERN = r'(a\s+couple\s+of|the|a|\d+)'

# Compiled regex for performance
REGEX_PATTERNS = [
    # Pattern 1: "3 hours ago", "a minute from now"
    re.compile(rf'{NUM_PATTERN}\s*{UNIT_PATTERN}\s*{DIRECTION_PATTERN}', re.IGNORECASE),
    # Pattern 2: "after 5min", "in 2 seconds"
    re.compile(rf'{DIRECTION_PATTERN}\s*{NUM_PATTERN}\s*{UNIT_PATTERN}', re.IGNORECASE),
    # Pattern 3: "10mins ago" (no space)
    re.compile(rf'(\d+)\s*({UNIT_PATTERN})\s*({DIRECTION_PATTERN})?', re.IGNORECASE)
]

# --- Helper Functions ---
def _is_numeric(s):
    """Checks if a string can be converted to a digit"""
    return s.isdigit()

def _parse_numeric_string(s):
    """Converts number words to digits"""
    return s.replace('a couple of', '2').replace('a', '1').replace('the', '1')

# --- Core Parsing Logic ---
def _parse_time_query(query):
    """Parses a natural language query to extract time information"""
    if not isinstance(query, str):
        return None
    lq = query.lower()

    for i, pattern in enumerate(REGEX_PATTERNS):
        match = pattern.search(lq)
        if not match:
            continue

        if i < 2:  # Patterns 1 and 2
            num_str = _parse_numeric_string(match.group(1 if i == 0 else 2))
            if _is_numeric(num_str):
                value = int(num_str)
                unit_str = match.group(2 if i == 0 else 3)
                direction = match.group(3 if i == 0 else 1)
            else:
                continue
        else:  # Pattern 3
            value = int(match.group(1))
            unit_str = match.group(2)
            direction = match.group(3) or 'from now'

        # Normalize unit for timedelta
        if unit_str.startswith('h'): unit = 'hours'
        elif unit_str.startswith('m'): unit = 'minutes'
        else: unit = 'seconds'

        return value, unit, (direction.lower() if direction else 'from now')

    return None

# --- Main Calculation Function ---
def calculate_time(query):
    """Calculates a new time based on a natural language query"""
    parsed_query = _parse_time_query(query)
    if not parsed_query:
        return "Invalid query format. Please use a valid format."

    value, unit, direction = parsed_query
    now = datetime.datetime.now()
    delta = datetime.timedelta(**{unit: value})

    if direction in ['ago', 'before', 'last', 'back']:
        new_time = now - delta
    else:  # from now, after, next, in
        new_time = now + delta

    return new_time.strftime("%H:%M:%S")

# --- Example Usage ---
if __name__ == "__main__":
    print(f"Current time: {datetime.datetime.now().strftime('%H:%M:%S')}")
    queries = [
        "What time will it be 2 hrs from now?",
        "What was the time 1 hr ago?",
        "In 10 minutes what will be the time?",
        "What was the time 5 mins back?",
        "After 10 seconds what is the time going to be?",
        "What was the time 10secs back?",
        "What is the time after a couple of hours?",
        "In a minute, what will the time be?",
        "Time before 1 second",
        "Tell me the time a minute ago",
        "Invalid query"
    ]

    for q in queries:
        print(f"Query: '{q}' -> Result: {calculate_time(q)}")
