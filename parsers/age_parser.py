import re
from typing import Dict, Optional

def parse_age(query: str) -> Dict[str, Optional[any]]:
    """
    Parses the query string to extract age and age comparison information.
    """
    age_details = {"age": None, "age_limit_identifier": None}
    
    age_pattern_match = re.search(r'(above|greater than|over|below|less than|under)?\s*(\d+)\s*years( old)?', query)
    if age_pattern_match:
        age_comparator_keyword = age_pattern_match.group(1)
        parsed_age = int(age_pattern_match.group(2))
        
        age_details["age"] = parsed_age
        
        if age_comparator_keyword:
            if age_comparator_keyword in ["above", "greater than", "over"]:
                age_details["age_limit_identifier"] = ">="
            elif age_comparator_keyword in ["below", "less than", "under"]:
                age_details["age_limit_identifier"] = "<="
                
    return age_details
