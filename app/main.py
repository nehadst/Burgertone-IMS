from app import create_app,db
from app import create_app, socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.sales_analyzer import SalesAnalyzer
from app.services.inventory_predictor import InventoryPredictor

app = create_app()

with app.app_context():
    db.create_all()

@app.get("/api/inventory/forecast")
async def get_forecast():
    analyzer = SalesAnalyzer()
    predictor = InventoryPredictor()
    
    # Get historical data
    data = analyzer.load_historical_data()
    
    # Make predictions
    predictions = predictor.predict(data)
    
    # Get AI insights
    insights = predictor.get_ai_insights(predictions, data['actual'])
    
    return {
        "predictions": predictions.tolist(),
        "insights": insights,
        "historical_data": data.to_dict()
    }

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)