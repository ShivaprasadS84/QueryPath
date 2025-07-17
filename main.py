import re
from datetime import datetime, timedelta
from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional, Dict
from fastapi.middleware.cors import CORSMiddleware

query_path_app = FastAPI()

origins = [
    "https://localhost:4200",
]

query_path_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchResponse(BaseModel):
    age: Optional[int] = None
    age_limit_identifier: Optional[str] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    is_range: bool
    time: Optional[str] = None
    time_range: Optional[Dict[str, str]] = None

@query_path_app.get("/search", response_model=SearchResponse)
def search(search_query_string: str = Query(..., alias="q")):
    search_result = {
        "age": None,
        "age_limit_identifier": None,
        "gender": None,
        "diagnosis": None,
        "is_range": False,
        "time": None,
        "time_range": None,
    }

    normalized_query = search_query_string.lower()

    age_pattern_match = re.search(r'(above|greater than|over|below|less than|under)?\s*(\d+)\s*years( old)?', normalized_query)
    if age_pattern_match:
        age_comparator_keyword = age_pattern_match.group(1)
        parsed_age = int(age_pattern_match.group(2))
        
        search_result["age"] = parsed_age
        
        if age_comparator_keyword:
            if age_comparator_keyword in ["above", "greater than", "over"]:
                search_result["age_limit_identifier"] = ">="
            elif age_comparator_keyword in ["below", "less than", "under"]:
                search_result["age_limit_identifier"] = "<="

    if "female" in normalized_query:
        search_result["gender"] = "female"
    elif "male" in normalized_query:
        search_result["gender"] = "male"

    time_pattern_match = re.search(r'last\s+(\d+)\s+(day|hour|week|month|minute)s?', normalized_query)
    if time_pattern_match:
        time_quantity = int(time_pattern_match.group(1))
        time_unit = time_pattern_match.group(2)

        if time_unit in ["day", "week", "month"]:
            search_result["is_range"] = True
            current_date = datetime.now()
            if time_unit == "day":
                time_delta = timedelta(days=time_quantity)
            elif time_unit == "week":
                time_delta = timedelta(weeks=time_quantity)
            elif time_unit == "month":
                # Approximation: 30 days per month
                time_delta = timedelta(days=time_quantity * 30)
            
            calculated_start_date = current_date - time_delta
            search_result["time_range"] = {
                "start_date": calculated_start_date.strftime("%d-%m-%Y"),
                "end_date": current_date.strftime("%d-%m-%Y"),
            }
        elif time_unit in ["hour", "minute"]:
            search_result["is_range"] = False
            current_date = datetime.now()
            search_result["time"] = current_date.strftime("%d-%m-%Y")

    return search_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(query_path_app, host="0.0.0.0", port=8000)
