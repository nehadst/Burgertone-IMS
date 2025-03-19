from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import os
import json
import math
import numpy as np
from app.services.sales_analyzer import SalesAnalyzer
from app.services.inventory_predictor import InventoryPredictor
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, ConfigDict

# Custom JSON encoder to handle NaN values
class NaNJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
            return None
        if isinstance(obj, np.float64) or isinstance(obj, np.float32):
            if np.isnan(obj) or np.isinf(obj):
                return None
            return float(obj)
        if isinstance(obj, np.int64) or isinstance(obj, np.int32):
            return int(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Custom JSONResponse class
class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            cls=NaNJSONEncoder,
        ).encode("utf-8")

# Initialize FastAPI app
app = FastAPI(title="Burgertone Inventory API", default_response_class=CustomJSONResponse)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
project_root = os.path.dirname(os.path.dirname(__file__))
credentials_path = os.path.join(project_root, "credentials", "burgertone-credentials.json")

analyzer = SalesAnalyzer(credentials_path=credentials_path)
predictor = InventoryPredictor()

# Pydantic models with better type definitions
class Prediction(BaseModel):
    date: str  # Changed from datetime to str for consistent formatting
    predicted_quantity: int

class PredictionResponse(BaseModel):
    item_name: str
    predictions: List[Prediction]
    historical_avg: float
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class HistoricalDataResponse(BaseModel):
    item_name: str
    dates: List[str]
    quantities: List[int]
    sales: List[float]

@app.on_event("startup")
async def startup_event():
    """Load and train model on startup"""
    try:
        print("Loading historical data and training model...")
        # Force reload data on startup
        df = analyzer.load_historical_data(force_reload=True)
        predictor.train(df)
        print("Model training completed")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise e

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Burgertone Inventory API"}

@app.get("/api/inventory/predictions/{days}", response_model=List[PredictionResponse])
async def get_predictions(days: int = 7):
    """Get inventory predictions for specified number of days"""
    try:
        # Load latest data (will use cache if available)
        df = analyzer.load_historical_data()
        
        # Get predictions
        predictions = predictor.predict(df, days_ahead=days)
        
        # Format response
        response = []
        for item, preds in predictions.items():
            historical_avg = df[df['item_name'] == item]['quantity'].mean()
            
            # Ensure dates are in string format (YYYY-MM-DD)
            formatted_predictions = []
            for p in preds:
                # Make sure date is a string
                date_str = p["date"] if isinstance(p["date"], str) else p["date"].strftime('%Y-%m-%d')
                formatted_predictions.append({
                    "date": date_str,
                    "predicted_quantity": p["predicted_quantity"]
                })
            
            response.append({
                "item_name": item,
                "predictions": formatted_predictions,
                "historical_avg": round(historical_avg, 2)
            })
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/historical/{item_name}", response_model=HistoricalDataResponse)
async def get_historical_data(item_name: str, days: Optional[int] = 30):
    """Get historical data for specific item"""
    try:
        # Use cached data
        df = analyzer.load_historical_data()
        
        # Filter data
        item_data = df[df['item_name'] == item_name].tail(days)
        
        # Format dates as strings
        formatted_dates = item_data['date'].dt.strftime('%Y-%m-%d').tolist()
        
        return {
            "item_name": item_name,
            "dates": formatted_dates,
            "quantities": item_data['quantity'].tolist(),
            "sales": item_data['sales'].tolist()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/insights/{item_name}")
async def get_item_insights(item_name: str):
    """Get AI insights for specific item"""
    try:
        # Use cached data
        df = analyzer.load_historical_data()
        predictions = predictor.predict(df, days_ahead=7)
        
        if item_name not in predictions:
            raise HTTPException(status_code=404, detail="Item not found")
            
        item_predictions = {item_name: predictions[item_name]}
        insights = predictor.get_ai_insights(item_predictions, df)
        
        return {"insights": insights}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/items")
async def get_items():
    """Get list of all menu items"""
    try:
        # Use cached data
        df = analyzer.load_historical_data()
        items = df['item_name'].unique().tolist()
        return {"items": items}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/refresh-data")
async def refresh_data():
    """Force refresh of the data cache"""
    try:
        # Clear data cache and reload data
        analyzer.clear_cache()
        df = analyzer.load_historical_data(force_reload=True)
        
        # Clear prediction cache
        predictor.clear_prediction_cache()
        
        # Retrain model with fresh data
        predictor.train(df)
        
        return {"status": "success", "message": "Data refreshed and model retrained"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))