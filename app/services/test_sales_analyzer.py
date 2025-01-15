import unittest
from datetime import datetime
from app.services.sales_analyzer import SalesAnalyzer

class TestSalesAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SalesAnalyzer()
    
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