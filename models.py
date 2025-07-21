from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Union

class AgeInfo(BaseModel):
    """Age information with different constraint types"""
    model_config = ConfigDict(extra='allow')
    
    type: str  # "exact", "range", "min", "max"
    value: Optional[int] = None  # for exact age
    min: Optional[int] = None  # for range/min constraints
    max: Optional[int] = None  # for range/max constraints

class TimeframeInfo(BaseModel):
    """Timeframe information - either single date or date range"""
    model_config = ConfigDict(extra='allow')
    
    # For single date
    date: Optional[str] = None  # YYYY-MM-DD format
    
    # For date range
    start_date: Optional[str] = None  # YYYY-MM-DD format
    end_date: Optional[str] = None  # YYYY-MM-DD format

class DiagnosisInfo(BaseModel):
    """Diagnosis information with SNOMED CT mapping"""
    model_config = ConfigDict(extra='allow')
    
    concept_id: str
    primary_term: str

class SearchResponse(BaseModel):
    """Response model matching patient_client.py output format"""
    model_config = ConfigDict(extra='allow')
    
    gender: Optional[str] = None  # "male", "female", or null
    age: Optional[AgeInfo] = None  # Age constraints or null
    diagnosis: Optional[Union[str, DiagnosisInfo]] = None  # String or structured diagnosis
    timeframe: Optional[TimeframeInfo] = None  # Temporal information or null
