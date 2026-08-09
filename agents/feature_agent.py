import pandas as pd
import numpy as np
from pipeline.state import ClaimState

class FeatureAgent:
    def __init__(self):
        # PMFBY & Agronomic Thresholds
        self.EXTREME_RAIN_THRESHOLD_MM = 50.0
        self.HEATWAVE_THRESHOLD_C = 40.0
        self.SOIL_DEFICIT_THRESHOLD = 0.3  # GWETROOT < 0.3 indicates severe stress
        self.BASE_TEMP_GDD = 10.0          # Base temp for Growing Degree Days (Crop dependent, standardizing to 10)
        self.HISTORICAL_MEAN_RAIN = 350.0  # Assumed historical seasonal baseline for anomaly (in mm)
        self.HISTORICAL_STD_RAIN = 100.0   # Standard deviation for z-scores

    def run(self, state: ClaimState) -> ClaimState:
        print(f"[{state.claim_id}] FeatureAgent: Engineering 25 agricultural features from time-series...")
        
        try:
            df = state.weather_data
            
            # 1. Base Aggregations (Means and Sums)
            features = {
                "PRECTOTCORR_agg": float(df['PRECTOTCORR'].sum()),
                "T2M_agg": float(df['T2M'].mean()),
                "T2M_MAX_agg": float(df['T2M_MAX'].mean()),
                "T2M_MIN_agg": float(df['T2M_MIN'].mean()),
                "ALLSKY_SFC_SW_DWN_agg": float(df['ALLSKY_SFC_SW_DWN'].mean()),
                "RH2M_agg": float(df['RH2M'].mean()),
                "WS2M_agg": float(df['WS2M'].mean()),
                "GWETROOT_agg": float(df['GWETROOT'].mean()),
            }

            # Handle EVPTRNS (Evapotranspiration) if missing from NASA fetch, fallback to temperature proxy
            if 'EVPTRNS' in df.columns:
                features["EVPTRNS_agg"] = float(df['EVPTRNS'].sum())
            else:
                # Hargreaves-Samani proxy for Evapotranspiration
                features["EVPTRNS_agg"] = float((df['T2M_MAX'] - df['T2M_MIN']).mean() * 15.0)

            # 2. Temperature Stress Metrics
            features["abs_tmax"] = float(df['T2M_MAX'].max())
            df['heat_stress'] = np.where(df['T2M_MAX'] > 35.0, df['T2M_MAX'] - 35.0, 0)
            features["heat_stress_daily_agg"] = float(df['heat_stress'].sum())
            
            # Growing Degree Days (GDD)
            df['gdd'] = np.where(df['T2M'] > self.BASE_TEMP_GDD, df['T2M'] - self.BASE_TEMP_GDD, 0)
            features["gdd_daily_agg"] = float(df['gdd'].sum())
            
            # 3. Extreme Event Counters
            features["heatwave_days"] = int((df['T2M_MAX'] > self.HEATWAVE_THRESHOLD_C).sum())
            features["extreme_rain_days"] = int((df['PRECTOTCORR'] > self.EXTREME_RAIN_THRESHOLD_MM).sum())
            features["soil_deficit_days"] = int((df['GWETROOT'] < self.SOIL_DEFICIT_THRESHOLD).sum())

            # 4. Drought & Water Metrics
            # Consecutive Dry Days (Rain < 1mm)
            is_dry = df['PRECTOTCORR'] < 1.0
            # Pandas trick to count consecutive True values
            dry_streaks = is_dry.groupby((~is_dry).cumsum()).sum()
            features["max_consecutive_dry_days"] = int(dry_streaks.max())

            # Water Balance (Rain - Evapotranspiration)
            features["water_balance"] = float(features["PRECTOTCORR_agg"] - features["EVPTRNS_agg"])
            
            # Anomalies and Z-Scores
            features["rainfall_anomaly_mm"] = float(features["PRECTOTCORR_agg"] - self.HISTORICAL_MEAN_RAIN)
            features["rainfall_z_score"] = float(features["rainfall_anomaly_mm"] / self.HISTORICAL_STD_RAIN)
            
            # Soil moisture z-score proxy (GWETROOT ranges 0 to 1, mean ~ 0.5, std ~ 0.2)
            features["soil_moisture_z_score"] = float((features["GWETROOT_agg"] - 0.5) / 0.2)

            # SPEI Proxy (Standardized Precipitation Evapotranspiration Index)
            # Simplified for pipeline: Z-score of water balance
            features["SPEI_proxy_z_score"] = float(features["water_balance"] / self.HISTORICAL_STD_RAIN)

            # 5. Compound Stress (Days with both extreme heat AND soil deficit)
            compound_mask = (df['T2M_MAX'] > 35.0) & (df['GWETROOT'] < self.SOIL_DEFICIT_THRESHOLD)
            features["compound_stress_days"] = int(compound_mask.sum())
            
            # Attach the categorical data required by the model
            features["district"] = state.district
            features["crop"] = state.crop
            features["season"] = state.season

            # Save to state
            state.engineered_features = features
            print(f"[{state.claim_id}] FeatureAgent: Successfully computed {len(features)} variables.")
            
        except Exception as e:
            state.status = "FAILED"
            state.error_message = f"Feature Engineering failed: {str(e)}"
            
        return state