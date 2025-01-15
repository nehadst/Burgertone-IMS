from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import os
from app.services.sales_analyzer import SalesAnalyzer
from app.services.inventory_predictor import InventoryPredictor
from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict

# Initialize FastAPI app
app = FastAPI(title="Burgertone Inventory API")

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
    date: datetime
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
        df = analyzer.load_historical_data()
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
        # Load latest data
        df = analyzer.load_historical_data()
        
        # Get predictions
        predictions = predictor.predict(df, days_ahead=days)
        
        # Format response
        response = []
        for item, preds in predictions.items():
            historical_avg = df[df['item_name'] == item]['quantity'].mean()
            response.append({
                "item_name": item,
                "predictions": [
                    {"date": p["date"], "predicted_quantity": p["predicted_quantity"]} 
                    for p in preds
                ],
                "historical_avg": round(historical_avg, 2)
            })
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/historical/{item_name}", response_model=HistoricalDataResponse)
async def get_historical_data(item_name: str, days: Optional[int] = 30):
    """Get historical data for specific item"""
    try:
        df = analyzer.load_historical_data()
        
        # Filter data
        item_data = df[df['item_name'] == item_name].tail(days)
        
        return {
            "item_name": item_name,
            "dates": item_data['date'].dt.strftime('%Y-%m-%d').tolist(),
            "quantities": item_data['quantity'].tolist(),
            "sales": item_data['sales'].tolist()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/insights/{item_name}")
async def get_item_insights(item_name: str):
    """Get AI insights for specific item"""
    try:
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
        df = analyzer.load_historical_data()
        items = df['item_name'].unique().tolist()
        return {"items": items}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))