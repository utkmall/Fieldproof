from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ClaimState(BaseModel):
    # Visible temporal and context inputs
    claim_id: str
    district: str
    crop: str
    season: str
    lat: float
    lon: float
    observation_start_date: str
    assessment_date: str
    
    status: str = "PROCESSING"
    error_message: Optional[str] = None
    
    # Weather QA & Feature Data
    weather_data: Optional[Any] = None
    weather_days_retrieved: int = 0
    missing_weather_values: int = 0
    imputation_used: bool = False
    engineered_features: Optional[Dict[str, float]] = None
    
    # ML Outputs & Evidence
    predicted_relative_yield: Optional[float] = None
    estimated_weather_linked_loss_percentage: Optional[float] = None
    weather_linked_loss_assessment: Optional[str] = None
    is_catastrophic: Optional[bool] = None
    
    # Operational Action
    final_action: Optional[str] = None
    reason_codes: list[str] = Field(default_factory=list)
    
    class Config:
        arbitrary_types_allowed = True