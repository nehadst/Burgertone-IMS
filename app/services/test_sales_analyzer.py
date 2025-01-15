import unittest
from datetime import datetime
import os
import pandas as pd
from app.services.sales_analyzer import SalesAnalyzer

class TestSalesAnalyzer(unittest.TestCase):
    def setUp(self):
        # Get project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Build path to credentials in the credentials folder
        credentials_path = os.path.join(project_root, "credentials", "burgertone-credentials.json")
        
        print(f"Looking for credentials at: {credentials_path}")  # Debug print
        
        if not os.path.exists(credentials_path):
            raise ValueError(f"Credentials file not found at: {credentials_path}")
        
        self.analyzer = SalesAnalyzer(credentials_path=credentials_path)
    
    def test_load_historical_data(self):
        """Test loading and processing historical data"""
        try:
            df = self.analyzer.load_historical_data()
            
            # Verify dataframe structure
            required_columns = ['item_name', 'quantity', 'sales', 'date']
            for col in required_columns:
                self.assertIn(col, df.columns)
            
            # Verify data types
            self.assertTrue(pd.api.types.is_datetime64_any_dtype(df['date']))
            self.assertTrue(pd.api.types.is_numeric_dtype(df['quantity']))
            self.assertTrue(pd.api.types.is_numeric_dtype(df['sales']))
            
            # Print summary stats
            print("\nData Summary:")
            print(f"Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"Total menu items: {df['item_name'].nunique()}")
            print(f"Total records: {len(df)}")
            
        except Exception as e:
            self.fail(f"Test failed with error: {e}") 