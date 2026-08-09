import joblib
import json
import os
import pandas as pd
import numpy as np
import __main__
from pipeline.state import ClaimState

def asymmetric_crop_loss(y_true, y_pred):
    residual = y_pred - y_true
    grad = residual.copy()
    hess = np.ones_like(residual)
    catastrophe_mask = (y_true < 0.6) & (residual > 0)
    PENALTY_MULTIPLIER = 5.0
    grad[catastrophe_mask] = residual[catastrophe_mask] * PENALTY_MULTIPLIER
    hess[catastrophe_mask] = PENALTY_MULTIPLIER
    return grad, hess

__main__.asymmetric_crop_loss = asymmetric_crop_loss

class MLAgent:
    def __init__(self, version="v1.0.0"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.base_path = os.path.join(project_root, version)
        
        self.regressor = joblib.load(os.path.join(self.base_path, "regressor.pkl"))
        self.classifier = joblib.load(os.path.join(self.base_path, "classifier.pkl"))
        
        with open(os.path.join(self.base_path, "metadata.json"), "r") as f:
            self.metadata = json.load(f)
            self.expected_features = self.metadata["features"]

    def run(self, state: ClaimState) -> ClaimState:
        try:
            features_df = pd.DataFrame([state.engineered_features])
            
            # 1. Check all metadata expected features exist
            missing_cols = set(self.expected_features) - set(features_df.columns)
            if missing_cols:
                raise ValueError(f"Missing expected features: {missing_cols}")
                
            # 2. Preserve exact metadata ordering
            features_df = features_df[self.expected_features]
            
            # 3. Exactly 25 columns
            if features_df.shape[1] != 25:
                raise ValueError(f"Expected 25 features, received {features_df.shape[1]}")
                
            # 4. No NaNs permitted
            if features_df.isnull().values.any():
                raise ValueError("NaN values detected in final ML feature matrix.")
            
            pred_yield = float(self.regressor.predict(features_df)[0])
            state.predicted_relative_yield = round(pred_yield, 4)
            
            # Derive estimated weather loss strictly mathematically
            state.estimated_weather_linked_loss_percentage = max(0.0, min(100.0, round((1 - pred_yield) * 100, 2)))
            
            state.is_catastrophic = bool(self.classifier.predict(features_df)[0])
            
        except Exception as e:
            state.status = "FAILED"
            state.error_message = f"ML Safety Check Failed: {str(e)}"
            
        return state