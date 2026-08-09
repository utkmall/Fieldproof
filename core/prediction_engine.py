import joblib
import json
import os
import pandas as pd
import numpy as np
import __main__

# ==========================================
# 1. THE CUSTOM ASYMMETRIC LOSS FUNCTION
# ==========================================
# We must redefine the exact math from Colab here so the pickled model can find it.
def asymmetric_crop_loss(y_true, y_pred):
    residual = y_pred - y_true
    grad = residual.copy()
    hess = np.ones_like(residual)
    
    catastrophe_mask = (y_true < 0.6) & (residual > 0)
    PENALTY_MULTIPLIER = 5.0
    
    grad[catastrophe_mask] = residual[catastrophe_mask] * PENALTY_MULTIPLIER
    hess[catastrophe_mask] = PENALTY_MULTIPLIER
    return grad, hess

# Inject it into Python's global namespace so joblib's unpickler doesn't panic
__main__.asymmetric_crop_loss = asymmetric_crop_loss
# ==========================================

class CropLossPredictor:
    def __init__(self, version="v1.0.0"):
        """Loads models into memory using absolute paths, bypassing the 'artifacts' folder."""
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_path = os.path.join(os.path.dirname(current_dir), version)
        
        print(f"DEBUG: I am strictly looking for models in: {self.base_path}")
        
        # Load Models (It will now successfully find the custom math above!)
        self.regressor = joblib.load(os.path.join(self.base_path, "regressor.pkl"))
        self.classifier = joblib.load(os.path.join(self.base_path, "classifier.pkl"))
        
        # Load Baselines
        with open(os.path.join(self.base_path, "crop_averages.json"), "r") as f:
            self.crop_averages = json.load(f)
            
        self.global_average = np.mean(list(self.crop_averages.values()))

    def estimate_loss_category(self, loss_percentage: float) -> str:
        """Applies PMFBY business logic tiers."""
        if loss_percentage < 15.0: return "No Claim"
        elif loss_percentage <= 30.0: return "Moderate Damage"
        elif loss_percentage <= 50.0: return "Severe Damage"
        else: return "Catastrophic Loss"

    def process_claim(self, claim_data: dict) -> dict:
        """Executes the end-to-end inference pipeline."""
        
        features_df = pd.DataFrame([claim_data])
        
        # Run Inference
        pred_relative_yield = self.regressor.predict(features_df)[0]
        is_catastrophic = bool(self.classifier.predict(features_df)[0])
        
        # Financial Translation
        hist_avg = self.crop_averages.get(claim_data['crop'], self.global_average)
        pred_actual_yield = pred_relative_yield * hist_avg
        
        loss_percentage = max(0.0, min(100.0, (1 - pred_relative_yield) * 100))
        damage_tier = self.estimate_loss_category(loss_percentage)
        
        recommendation = "MANUAL REVIEW"
        if is_catastrophic and loss_percentage > 50:
            recommendation = "APPROVE"
        elif loss_percentage < 15:
            recommendation = "REJECT"

        return {
            "historical_average_kg_ha": round(hist_avg, 2),
            "predicted_relative_yield": round(float(pred_relative_yield), 3),
            "predicted_actual_yield_kg_ha": round(float(pred_actual_yield), 2),
            "estimated_loss_percentage": round(float(loss_percentage), 2),
            "damage_tier": damage_tier,
            "catastrophic_failure_detected": is_catastrophic,
            "recommendation": recommendation
        }