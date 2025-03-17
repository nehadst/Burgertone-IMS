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
            
            # Print detailed menu item analysis
            print("\n=== Menu Items Analysis ===")
            
            # Group by item_name and get total quantities and sales
            item_summary = df.groupby('item_name').agg({
                'quantity': ['sum', 'mean'],
                'sales': ['sum', 'mean']
            }).round(2)
            
            # Rename columns for clarity
            item_summary.columns = ['total_qty', 'avg_daily_qty', 'total_sales', 'avg_daily_sales']
            
            # Sort by total sales descending
            item_summary = item_summary.sort_values('total_sales', ascending=False)
            
            print("\nTop 10 Items by Sales:")
            print(item_summary.head(10))
            
            print("\nSample of Daily Data:")
            print(df.head(10))
            
            # Basic statistics
            print("\nOverall Statistics:")
            print(f"Date range: {df['date'].min()} to {df['date'].max()}")
            print(f"Total menu items: {df['item_name'].nunique()}")
            print(f"Total records: {len(df)}")
            
        except Exception as e:
            self.fail(f"Test failed with error: {e}") 