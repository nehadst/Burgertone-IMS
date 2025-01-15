import unittest
import pandas as pd
from datetime import datetime, timedelta
from app.services.sales_analyzer import SalesAnalyzer
from app.services.inventory_predictor import InventoryPredictor
import os

class TestInventoryPredictor(unittest.TestCase):
    def setUp(self):
        # Get credentials path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        credentials_path = os.path.join(project_root, "credentials", "burgertone-credentials.json")
        
        # Initialize analyzer and predictor
        self.analyzer = SalesAnalyzer(credentials_path=credentials_path)
        self.predictor = InventoryPredictor()
        
    def test_inventory_prediction(self):
        """Test the full prediction pipeline"""
        try:
            # Load historical data
            df = self.analyzer.load_historical_data()
            
            # Train the model
            self.predictor.train(df)
            
            # Make predictions for next 7 days
            predictions = self.predictor.predict(df, days_ahead=7)
            
            # Get AI insights
            insights = self.predictor.get_ai_insights(predictions, df)
            
            # Print results
            print("\n=== Inventory Predictions ===")
            for item, preds in predictions.items():
                print(f"\n{item}:")
                for pred in preds:
                    print(f"  {pred['date'].strftime('%Y-%m-%d')}: {pred['predicted_quantity']} units")
            
            print("\n=== AI Insights ===")
            print(insights)
            
            # Basic validations
            self.assertIsNotNone(predictions)
            self.assertTrue(len(predictions) > 0)
            
        except Exception as e:
            self.fail(f"Test failed with error: {e}") 