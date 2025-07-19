from pydantic import BaseModel
from typing import Optional, Dict

class SearchResponse(BaseModel):
    age: Optional[int] = None
    age_limit_identifier: Optional[str] = None
    gender: Optional[str] = None
    diagnosis: Optional[str] = None
    is_range: bool
    time: Optional[str] = None
    time_range: Optional[Dict[str, str]] = None
