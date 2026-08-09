from pipeline.state import ClaimState
from datetime import datetime

class ValidationAgent:
    def run(self, state: ClaimState) -> ClaimState:
        try:
            start = datetime.strptime(state.observation_start_date, "%Y-%m-%d").date()
            assess = datetime.strptime(state.assessment_date, "%Y-%m-%d").date()
            today = datetime.utcnow().date()
            
            if assess < start:
                state.status = "FAILED"
                state.error_message = "Assessment date cannot precede observation start date."
                return state
                
            if assess > today:
                state.status = "FAILED"
                state.error_message = "Assessment date cannot be in the future."
                return state
                
        except ValueError:
            state.status = "FAILED"
            state.error_message = "Dates must be provided in valid YYYY-MM-DD format."
            return state

        return state