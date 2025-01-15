from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv
import os

class InventoryPredictor:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Get OpenAI key from .env
        openai_key = os.getenv('OPENAI_API_KEY')
        if not openai_key:
            print("Warning: OPENAI_API_KEY not found in .env file")
        
        self.openai = openai.OpenAI(api_key=openai_key)
        
    def prepare_features(self, df):
        """Prepare features for ML model"""
        # Create time-based features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6]).astype(int)
        
        # Calculate rolling averages
        df['qty_7day_avg'] = df.groupby('item_name')['quantity'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        df['qty_30day_avg'] = df.groupby('item_name')['quantity'].transform(
            lambda x: x.rolling(window=30, min_periods=1).mean()
        )
        
        # Add lag features
        df['qty_prev_day'] = df.groupby('item_name')['quantity'].shift(1)
        df['qty_prev_week'] = df.groupby('item_name')['quantity'].shift(7)
        
        # Fill NaN values
        df = df.fillna({
            'qty_prev_day': 0,
            'qty_prev_week': 0,
            'qty_7day_avg': 0,
            'qty_30day_avg': 0
        })
        
        return df
        
    def train(self, df):
        """Train the model on historical data"""
        print("Training inventory prediction model...")
        
        # Prepare features
        df = self.prepare_features(df)
        
        # Features for training
        feature_columns = [
            'day_of_week',
            'month',
            'is_weekend',
            'qty_7day_avg',
            'qty_30day_avg',
            'qty_prev_day',
            'qty_prev_week'
        ]
        
        # Train a separate model for each menu item
        self.models = {}
        self.scalers = {}
        
        # Filter out null item names
        valid_items = df['item_name'].dropna().unique()
        
        for item in valid_items:  # Changed from df['item_name'].unique()
            print(f"Training model for: {item}")
            item_data = df[df['item_name'] == item]
            
            # Skip if not enough data
            if len(item_data) < 10:  # Minimum required samples
                print(f"Skipping {item} - insufficient data")
                continue
            
            X = item_data[feature_columns]
            y = item_data['quantity']
            
            try:
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X_train_scaled, y_train)
                
                # Store model and scaler
                self.models[item] = model
                self.scalers[item] = scaler
                
                # Print model performance
                train_score = model.score(X_train_scaled, y_train)
                test_score = model.score(X_test_scaled, y_test)
                print(f"  Train R² score: {train_score:.3f}")
                print(f"  Test R² score: {test_score:.3f}")
                
            except Exception as e:
                print(f"Error training model for {item}: {str(e)}")
                continue
    
    def predict(self, df, days_ahead=7):
        """Predict inventory needs for the next n days"""
        predictions = {}
        
        # Get the last date in the dataset
        last_date = df['date'].max()
        
        # Prepare features for prediction
        df = self.prepare_features(df)
        
        for item in self.models.keys():
            item_predictions = []
            current_df = df[df['item_name'] == item].copy()
            
            # Predict for each day
            for i in range(days_ahead):
                next_date = last_date + timedelta(days=i+1)
                
                # Create feature row for prediction
                pred_features = pd.DataFrame({
                    'day_of_week': [next_date.dayofweek],
                    'month': [next_date.month],
                    'is_weekend': [1 if next_date.dayofweek in [5, 6] else 0],
                    'qty_7day_avg': [current_df['quantity'].tail(7).mean()],
                    'qty_30day_avg': [current_df['quantity'].tail(30).mean()],
                    'qty_prev_day': [current_df['quantity'].iloc[-1]],
                    'qty_prev_week': [current_df['quantity'].iloc[-7] if len(current_df) > 7 else 0]
                })
                
                # Scale features
                pred_features_scaled = self.scalers[item].transform(pred_features)
                
                # Make prediction
                pred_qty = self.models[item].predict(pred_features_scaled)[0]
                
                item_predictions.append({
                    'date': next_date,
                    'predicted_quantity': max(0, round(pred_qty))  # Ensure non-negative
                })
                
            predictions[item] = item_predictions
            
        return predictions
        
    def get_ai_insights(self, predictions, actual_data):
        """Get OpenAI analysis of predictions"""
        # Prepare data for analysis
        analysis_text = "Inventory Prediction Analysis:\n\n"
        
        for item, preds in predictions.items():
            analysis_text += f"Item: {item}\n"
            analysis_text += f"Predicted quantities: {[p['predicted_quantity'] for p in preds]}\n"
            analysis_text += f"Historical average: {actual_data[actual_data['item_name'] == item]['quantity'].mean():.1f}\n\n"
        
        prompt = f"""
        Analyze these inventory predictions:
        {analysis_text}
        
        Please provide:
        1. Key insights about predicted demand
        2. Potential risks or anomalies
        3. Specific inventory recommendations
        4. Factors that might affect these predictions
        """
        
        try:
            response = self.openai.chat.completions.create(
                model="o1-preview-2024-09-12",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error getting AI insights: {str(e)}" 