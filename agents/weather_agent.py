import httpx
import pandas as pd
from pipeline.state import ClaimState

class WeatherAgent:
    def __init__(self):
        self.base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.parameters = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,ALLSKY_SFC_SW_DWN,RH2M,WS2M,GWETROOT"
        self.MAX_MISSING_PERCENTAGE = 10.0 

    async def run(self, state: ClaimState) -> ClaimState:
        start_fmt = state.observation_start_date.replace("-", "")
        end_fmt = state.assessment_date.replace("-", "")

        params = {
            "parameters": self.parameters,
            "community": "AG",
            "longitude": state.lon,
            "latitude": state.lat,
            "start": start_fmt, 
            "end": end_fmt,     
            "format": "JSON"
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status() 
                
            data = response.json()
            df = pd.DataFrame(data['properties']['parameter'])
            df.index = pd.to_datetime(df.index, format='%Y%m%d')
            df.index.name = 'Date'
            
            total_cells = df.size
            missing_count = int((df == -999.0).sum().sum())
            state.missing_weather_values = missing_count
            state.imputation_used = missing_count > 0
            
            if total_cells > 0:
                missing_pct = (missing_count / total_cells) * 100
                if missing_pct > self.MAX_MISSING_PERCENTAGE:
                    state.status = "FAILED"
                    state.error_message = f"Weather data quality failure. {missing_pct:.1f}% missing values exceeds {self.MAX_MISSING_PERCENTAGE}% limit."
                    return state
            
            df = df.replace(-999.0, pd.NA).interpolate(method='linear').ffill().bfill() 
            state.weather_data = df
            state.weather_days_retrieved = len(df)
            
        except Exception as e:
            state.status = "FAILED"
            state.error_message = f"Weather data retrieval error: {str(e)}"
            
        return state