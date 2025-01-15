import unittest
import pandas as pd
from datetime import datetime, timedelta
from app.services.sales_analyzer import SalesAnalyzer
from app.services.inventory_predictor import InventoryPredictor
import os

class TestInventoryPredictor(unittest.TestCase):
    def setUp(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        credentials_path = os.path.join(project_root, "credentials", "burgertone-credentials.json")
        
        self.analyzer = SalesAnalyzer(credentials_path=credentials_path)
        self.predictor = InventoryPredictor()
        
    def test_inventory_prediction(self):
        """Test the full prediction pipeline"""
        try:
            # Load historical data
            df = self.analyzer.load_historical_data()
            
            print("\n========== HISTORICAL DATA SUMMARY ==========")
            # Show recent history for each item
            for item in df['item_name'].unique():
                if pd.isna(item):
                    continue
                recent_data = df[df['item_name'] == item].tail(7)
                if not recent_data.empty:
                    print(f"\n{item}:")
                    print("Last 7 days quantities:", recent_data['quantity'].tolist())
                    print(f"Average daily quantity: {recent_data['quantity'].mean():.1f}")
            
            # Train the model
            print("\n========== TRAINING MODELS ==========")
            self.predictor.train(df)
            
            # Make predictions
            print("\n========== PREDICTIONS FOR NEXT 7 DAYS ==========")
            predictions = self.predictor.predict(df, days_ahead=7)
            
            # Display predictions in a clear format
            for item, preds in predictions.items():
                print(f"\n{item}:")
                print("Date         | Predicted Quantity")
                print("-" * 30)
                for pred in preds:
                    date_str = pred['date'].strftime('%Y-%m-%d')
                    qty = pred['predicted_quantity']
                    print(f"{date_str} | {qty:3d}")
            
            # Get and display AI insights
            print("\n========== AI INSIGHTS ==========")
            insights = self.predictor.get_ai_insights(predictions, df)
            print(insights)
            
            # Basic validations
            self.assertIsNotNone(predictions)
            self.assertTrue(len(predictions) > 0)
            
        except Exception as e:
            self.fail(f"Test failed with error: {e}")

if __name__ == '__main__':
    unittest.main() 