from typing import Optional

def parse_gender(query: str) -> Optional[str]:
    """
    Parses the query string to extract gender information.
    """
    if "female" in query:
        return "female"
    elif "male" in query:
        return "male"
    return None
