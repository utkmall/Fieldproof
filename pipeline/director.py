from pipeline.state import ClaimState
from agents.validation_agent import ValidationAgent
from agents.weather_agent import WeatherAgent
from agents.feature_agent import FeatureAgent
from agents.ml_agent import MLAgent
from agents.decision_agent import DecisionAgent

class ClaimDirector:
    def __init__(self):
        # Instantiate all agents
        self.validation_agent = ValidationAgent()
        self.weather_agent = WeatherAgent()
        self.feature_agent = FeatureAgent()
        self.ml_agent = MLAgent()
        self.decision_agent = DecisionAgent()

    async def process_claim(self, payload: dict) -> ClaimState:
        print(f"\n--- Starting Pipeline Execution for Claim: {payload.get('claim_id')} ---")
        
        state = ClaimState(**payload)
        
        state = self.validation_agent.run(state)
        if state.status == "FAILED": return state
            
        state = await self.weather_agent.run(state)
        if state.status == "FAILED": return state
            
        state = self.feature_agent.run(state)
        if state.status == "FAILED": return state
            
        state = self.ml_agent.run(state)
        if state.status == "FAILED": return state
            
        # Final Step: Business Logic
        state = self.decision_agent.run(state)
        if state.status == "FAILED":
            print(f"!!! Pipeline Aborted: {state.error_message} !!!\n")
            return state
            
        print(f"--- Pipeline Execution Successfully Completed ---\n")
        return state