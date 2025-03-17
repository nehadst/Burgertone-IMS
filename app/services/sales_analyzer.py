from google.cloud import storage
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO
import numpy as np
import json
import os

class SalesAnalyzer:
    def __init__(self, bucket_name="burgertone", credentials_path=None):
        if credentials_path:
            self.storage_client = storage.Client.from_service_account_json(credentials_path)
        else:
            # Try to get credentials from environment variable
            credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_json:
                self.storage_client = storage.Client.from_service_account_info(
                    json.loads(credentials_json)
                )
            else:
                raise ValueError(
                    "No credentials provided. Either pass credentials_path or "
                    "set GOOGLE_APPLICATION_CREDENTIALS environment variable"
                )
        self.bucket = self.storage_client.bucket(bucket_name)
        
        # Cache for historical data
        self._historical_data_cache = None
        self._last_cache_time = None
        self._cache_expiry = timedelta(hours=6)  # Refresh cache every 6 hours
        
    def load_historical_data(self, force_reload=False):
        """Load all CSV files from GCS and combine them"""
        current_time = datetime.now()
        
        # Check if we have valid cached data
        if not force_reload and self._historical_data_cache is not None and self._last_cache_time is not None:
            # If cache is still valid (less than cache_expiry old)
            if current_time - self._last_cache_time < self._cache_expiry:
                print("Using cached historical data")
                return self._historical_data_cache
        
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
        
        # Update cache
        self._historical_data_cache = combined_df
        self._last_cache_time = current_time
        
        return combined_df
    
    def _extract_menu_items(self, df):
        """Extract menu items sales data from CSV content"""
        try:
            # Convert content to string to search for sections
            content = df.to_string()
            
            # Find the SALES BY MENU ITEM section
            if 'SALES BY MENU ITEM' not in content:
                print("SALES BY MENU ITEM section not found")
                return None
            
            # Create DataFrame with correct columns and dtypes
            menu_items = pd.DataFrame({
                'item_name': pd.Series(dtype='str'),
                'quantity': pd.Series(dtype='int'),
                'sales': pd.Series(dtype='float'),
                'date': pd.Series(dtype='datetime64[ns]')
            })
            
            # Find rows between "SALES BY MENU ITEM" and the next section
            menu_item_started = False
            for index, row in df.iterrows():
                # Check if we've reached the menu items section
                if 'SALES BY MENU ITEM' in str(row.values):
                    menu_item_started = True
                    continue
                
                # Skip header row
                if menu_item_started and 'Menu Item' in str(row.values):
                    continue
                
                # Stop if we hit the next section
                if menu_item_started and row.isna().all():
                    break
                
                # Process menu item row
                if menu_item_started:
                    try:
                        # Use iloc instead of positional indexing
                        item_name = row.iloc[0]
                        sales = float(str(row.iloc[1]).replace('$', '').replace(',', ''))
                        quantity = int(float(row.iloc[2]))
                        
                        # Create new row with correct dtypes
                        new_row = pd.DataFrame({
                            'item_name': [item_name],
                            'quantity': [quantity],
                            'sales': [sales],
                            'date': [df['date'].iloc[0]]
                        })
                        
                        # Append to existing DataFrame
                        menu_items = pd.concat([menu_items, new_row], ignore_index=True)
                        
                    except (ValueError, IndexError) as e:
                        print(f"Skipping row due to error: {e}")
                        continue
            
            return menu_items
            
        except Exception as e:
            print(f"Error extracting menu items: {str(e)}")
            print(f"DataFrame head:\n{df.head()}")
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
        
    def clear_cache(self):
        """Clear the data cache to force reload on next call"""
        self._historical_data_cache = None
        self._last_cache_time = None
        print("Historical data cache cleared")