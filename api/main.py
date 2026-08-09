from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from pipeline.director import ClaimDirector
import uuid
import datetime
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

app = FastAPI(title="PMFBY Risk Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

director = ClaimDirector()

class ClaimPayload(BaseModel):
    district: str
    crop: str
    season: str
    lat: float
    lon: float
    observation_start_date: str
    assessment_date: str

@app.post("/v1/plugin/assess_claim")
async def verify_claim(request: ClaimPayload):
    req_dict = request.model_dump()
    req_dict["claim_id"] = f"CLM-{str(uuid.uuid4())[:8].upper()}"
    
    final_state = await director.process_claim(req_dict)
    
    if final_state.status == "FAILED":
        raise HTTPException(status_code=422, detail=final_state.error_message)
        
    response = {
        "claim_id": final_state.claim_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "status": "PROCESSED",
        "input_context": {
            "district": final_state.district,
            "crop": final_state.crop,
            "season": final_state.season,
            "observation_start_date": final_state.observation_start_date,
            "assessment_date": final_state.assessment_date
        },
        "model_assessment": {
            "predicted_relative_yield": final_state.predicted_relative_yield,
            "estimated_weather_linked_loss_percentage": final_state.estimated_weather_linked_loss_percentage,
            "weather_linked_loss_assessment": final_state.weather_linked_loss_assessment,
            "catastrophic_failure_detected": final_state.is_catastrophic
        },
        "operational_assessment": {
            "action": final_state.final_action,
            "reason_codes": final_state.reason_codes
        },
        "processing_metadata": {
            "model_version": "v1.0.0",
            "weather_provider": "NASA POWER",
            "weather_start_date": final_state.observation_start_date,
            "weather_end_date": final_state.assessment_date,
            "weather_days_analyzed": final_state.weather_days_retrieved,
            "processed_features": len(final_state.engineered_features) if final_state.engineered_features else 0,
            "missing_weather_values": final_state.missing_weather_values,
            "imputation_used": final_state.imputation_used
        }
    }
        
    return response