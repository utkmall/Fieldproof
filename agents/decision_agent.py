from pipeline.state import ClaimState

class DecisionAgent:
    def run(self, state: ClaimState) -> ClaimState:
        try:
            loss = state.estimated_weather_linked_loss_percentage
            is_catas = state.is_catastrophic
            
            # 1. Map Model Evidence Tier
            if loss < 15.0:
                state.weather_linked_loss_assessment = "NO_SIGNIFICANT_LOSS_SIGNAL"
            elif 15.0 <= loss <= 30.0:
                state.weather_linked_loss_assessment = "MODERATE_LOSS_SIGNAL"
            elif 30.0 < loss <= 50.0:
                state.weather_linked_loss_assessment = "SEVERE_LOSS_SIGNAL"
            else:
                state.weather_linked_loss_assessment = "CATASTROPHIC_LOSS_SIGNAL"

            # 2. Map Operational Action strictly from evidence
            if loss < 15.0 and not is_catas:
                state.final_action = "NO_WEATHER_SUPPORTED_LOSS_SIGNAL"
                state.reason_codes.append("MODEL_LOW_WEATHER_LOSS")
                
            elif loss > 50.0 or is_catas:
                state.final_action = "WEATHER_SUPPORTED_LOSS_SIGNAL"
                if is_catas:
                    state.reason_codes.append("CATASTROPHIC_CLASSIFIER_POSITIVE")
                if loss > 50.0:
                    state.reason_codes.append("MODEL_HIGH_WEATHER_LOSS")
                    
            else:
                # Loss is between 15 and 50, and not catastrophic
                state.final_action = "MANUAL_REVIEW_REQUIRED"
                state.reason_codes.append("AMBIGUOUS_MODEL_EVIDENCE")
                
            state.status = "COMPLETED"
            
        except Exception as e:
            state.status = "FAILED"
            state.error_message = f"Decision logic failed: {str(e)}"
            
        return state