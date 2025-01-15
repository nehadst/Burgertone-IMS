from google.cloud import storage
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO
import numpy as np

class SalesAnalyzer:
    def __init__(self, bucket_name="burgertone"):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        
    def load_historical_data(self):
        """Load all CSV files from GCS and combine them"""
        print("Loading historical data from GCS...")
        dfs = []
        
        for blob in self.bucket.list_blobs(prefix="reports/"):
            try:
                print(f"Processing {blob.name}...")
                content = blob.download_as_text()
                
                # Parse the date from the filename
                date_str = blob.name.split('/')[-1].replace('.csv', '')
                
                # Read CSV content
                df = pd.read_csv(StringIO(content))
                
                # Add date column
                df['date'] = pd.to_datetime(date_str)
                
                # Extract sales data from SALES BY MENU ITEM section
                menu_items = self._extract_menu_items(df)
                if menu_items is not None:
                    dfs.append(menu_items)
                    
            except Exception as e:
                print(f"Error processing {blob.name}: {e}")
                continue
        
        if not dfs:
            raise ValueError("No valid data found in CSV files")
            
        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"Loaded data for {len(dfs)} days")
        return combined_df
    
    def _extract_menu_items(self, df):
        """Extract menu items sales data from CSV content"""
        try:
            # Convert df to string to search for section
            content = df.to_string()
            
            # Find the SALES BY MENU ITEM section
            if 'SALES BY MENU ITEM' not in content:
                return None
                
            # Extract relevant columns
            menu_items = pd.DataFrame({
                'item_name': df['Menu Item'],
                'quantity': df['Quantity'].astype(int),
                'sales': df['Sales Total'].str.replace('$', '').str.replace(',', '').astype(float),
                'date': df['date']
            })
            
            return menu_items
            
        except Exception as e:
            print(f"Error extracting menu items: {e}")
            return None
    
    def prepare_for_forecasting(self, df):
        """Process data for ML model"""
        print("Preparing data for forecasting...")
        
        # Add time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Calculate rolling statistics
        df['prev_day_sales'] = df.groupby('item_name')['quantity'].shift(1)
        df['prev_week_sales'] = df.groupby('item_name')['quantity'].shift(7)
        df['moving_avg_7d'] = df.groupby('item_name')['quantity'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        
        # Fill missing values
        df = df.fillna({
            'prev_day_sales': 0,
            'prev_week_sales': 0,
            'moving_avg_7d': 0
        })
        
        print("Data preparation completed")
        return df

    def get_summary_stats(self, df):
        """Get summary statistics for each menu item"""
        stats = df.groupby('item_name').agg({
            'quantity': ['mean', 'std', 'min', 'max', 'sum'],
            'sales': ['sum', 'mean']
        }).round(2)
        
        stats.columns = ['avg_daily_qty', 'std_qty', 'min_qty', 'max_qty', 
                        'total_qty', 'total_sales', 'avg_daily_sales']
        return stats