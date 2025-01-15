from google.cloud import storage
import pandas as pd
from datetime import datetime
import numpy as np

class SalesAnalyzer:
    def __init__(self, bucket_name="burgertone"):
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(bucket_name)
        
    def load_historical_data(self):
        """Load all CSV files from GCS and combine them"""
        dfs = []
        for blob in self.bucket.list_blobs(prefix="reports/"):
            content = blob.download_as_text()
            df = pd.read_csv(StringIO(content))
            date = blob.name.split('/')[-1].replace('.csv', '')
            df['date'] = pd.to_datetime(date)
            dfs.append(df)
        
        return pd.concat(dfs)
        
    def prepare_for_forecasting(self, df):
        """Process data for ML model"""
        # Extract relevant features
        features = [
            'day_of_week',
            'month',
            'is_weekend',
            'is_holiday',
            'previous_day_sales',
            'previous_week_sales',
            'moving_average_7d'
        ]