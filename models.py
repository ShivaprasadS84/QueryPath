from pydantic import BaseModel, ConfigDict
from typing import Optional, Any

class TemporalInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    type: Optional[str] = None
    date: Optional[Any] = None  # for single_date - can be string or date
    start_date: Optional[Any] = None  # for date_range - can be string or date
    end_date: Optional[Any] = None  # for date_range - can be string or date

class AgeInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    type: Optional[str] = None
    value: Optional[Any] = None  # for exact
    min: Optional[Any] = None  # for range/min
    max: Optional[Any] = None  # for range/max

class PatientInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    gender: Optional[Any] = None
    age: Optional[Any] = None  # Can be AgeInfo dict or None
    diagnosis: Optional[Any] = None

class ErrorInfo(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    source: Optional[str] = None
    error: Optional[str] = None

class SearchResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    
    temporal_info: Optional[Any] = None
    patient_info: Optional[Any] = None
    errors: Optional[Any] = None
