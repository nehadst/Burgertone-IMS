from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import openai

class InventoryPredictor:
    def __init__(self):
        # Initialize OpenAI with API key from environment
        self.openai = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Default model parameters
        self.rf_params = {
            'n_estimators': 100,
            'max_depth': 5,
            'min_samples_split': 5,
            'min_samples_leaf': 3,
            'random_state': 42
        }
        self.min_data_points = 30  # Minimum days of data required
        self.scaler = StandardScaler()
        
    def prepare_features(self, df):
        """Prepare features with improved feature engineering"""
        # Basic calendar features
        df['day_of_week'] = df['date'].dt.dayofweek
        df['month'] = df['date'].dt.month
        df['is_weekend'] = df['date'].dt.dayofweek.isin([5, 6]).astype(int)
        
        # Improved rolling averages
        for window in [3, 7, 14]:
            df[f'qty_{window}day_avg'] = df.groupby('item_name')['quantity'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df[f'qty_{window}day_std'] = df.groupby('item_name')['quantity'].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            )
        
        # Lag features
        df['qty_prev_day'] = df.groupby('item_name')['quantity'].shift(1)
        df['qty_prev_week'] = df.groupby('item_name')['quantity'].shift(7)
        
        # Fill missing values with rolling means
        fill_columns = [col for col in df.columns if col.startswith('qty_')]
        for col in fill_columns:
            df[col] = df.groupby('item_name')[col].transform(
                lambda x: x.fillna(x.rolling(window=7, min_periods=1).mean())
            )
        
        # Replace any remaining NaN with 0
        df = df.fillna(0)
        
        return df
        
    def train(self, df):
        """Train models with improved validation"""
        print("Training inventory prediction model...")
        
        # Standardize item names first
        df = self._standardize_item_names(df)
        
        # Then prepare features
        df = self.prepare_features(df)
        
        feature_columns = [
            'day_of_week',
            'month',
            'is_weekend',
            'qty_3day_avg',
            'qty_7day_avg',
            'qty_14day_avg',
            'qty_3day_std',
            'qty_7day_std',
            'qty_14day_std',
            'qty_prev_day',
            'qty_prev_week'
        ]
        
        self.models = {}
        self.scalers = {}
        self.feature_columns = feature_columns
        
        # Group similar items
        item_groups = self._group_similar_items(df)
        
        for item in df['item_name'].unique():
            print(f"\nAnalyzing {item}")
            item_data = df[df['item_name'] == item].copy()
            
            if len(item_data) < self.min_data_points:
                print(f"Skipping {item} - insufficient data (only {len(item_data)} points)")
                continue
            
            # Prepare X (features) and y (target)
            X = item_data[feature_columns].copy()
            
            # Add group features if available
            group_features = self._get_group_features(item, item_groups, df)
            if group_features is not None:
                X = X.reset_index(drop=True)
                group_features = group_features.reset_index(drop=True)
                X = pd.concat([X, group_features], axis=1)
            
            y = item_data['quantity'].reset_index(drop=True)
            
            # Fill NaN values with mean of each column
            for column in X.columns:
                X[column] = X[column].fillna(X[column].mean())
                # If column is all NaN, fill with 0
                if pd.isna(X[column]).all():
                    X[column] = X[column].fillna(0)
            
            # Verify no NaN values remain
            if X.isna().any().any():
                print(f"Skipping {item} - cannot handle remaining NaN values")
                continue
            
            print(f"Features shape: {X.shape}")
            print(f"Target shape: {y.shape}")
            
            if X.shape[0] != y.shape[0]:
                print(f"Skipping {item} - feature/target mismatch")
                continue
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Try both models
            rf_model = RandomForestRegressor(**self.rf_params)
            lr_model = LinearRegression()
            
            rf_model.fit(X_train_scaled, y_train)
            lr_model.fit(X_train_scaled, y_train)
            
            # Compare models
            rf_test_score = rf_model.score(X_test_scaled, y_test)
            lr_test_score = lr_model.score(X_test_scaled, y_test)
            
            if rf_test_score > lr_test_score:
                model = rf_model
                test_score = rf_test_score
                model_type = "Random Forest"
            else:
                model = lr_model
                test_score = lr_test_score
                model_type = "Linear Regression"
            
            if test_score > 0.3:
                self.models[item] = model
                self.scalers[item] = scaler
                
                print(f"Selected {model_type} model:")
                print(f"  Test R² score: {test_score:.3f}")
                
                if isinstance(model, RandomForestRegressor):
                    importances = dict(zip(X.columns, model.feature_importances_))
                    print("  Top 5 important features:")
                    for feat, imp in sorted(importances.items(), key=lambda x: x[1], reverse=True)[:5]:
                        print(f"    {feat}: {imp:.3f}")
            else:
                print(f"Skipping {item} - poor model performance (R² = {test_score:.3f})")
    
    def _group_similar_items(self, df):
        """Group similar items for additional features"""
        # Convert item names to strings and get unique values
        unique_items = df['item_name'].astype(str).unique()
        
        groups = {
            'burgers': [item for item in unique_items if 'burger' in item.lower()],
            'combos': [item for item in unique_items if 'combo' in item.lower()],
            'meals': [item for item in unique_items if 'meal' in item.lower()]
        }
        
        print("Found groups:")
        for group, items in groups.items():
            print(f"{group}: {len(items)} unique items")
            print(f"Example items: {items[:3]}")
        
        return groups
    
    def _get_group_features(self, item, groups, df):
        """Create features based on item groups"""
        for group_name, group_items in groups.items():
            if item in group_items:
                # Get the item's data first
                item_data = df[df['item_name'] == item]
                
                # Get group data
                group_df = df[df['item_name'].isin(group_items)]
                
                # Calculate group stats by date
                group_data = (group_df
                             .groupby('date')['quantity']
                             .agg(['mean', 'std'])
                             .reset_index())  # Reset index to use date as column
                
                # Merge with item data on date
                merged_data = pd.merge(
                    item_data[['date']],  # Only keep date from item_data
                    group_data,
                    on='date',
                    how='left'
                )
                
                # Drop the date column and rename features
                group_features = merged_data.drop('date', axis=1)
                group_features.columns = [f'group_{group_name}_{col}' for col in group_features.columns]
                
                print(f"Item data shape: {item_data.shape}")
                print(f"Group features shape: {group_features.shape}")
                
                return group_features
                
        return None
    
    def predict(self, df, days_ahead=7):
        """Generate predictions with NaN handling"""
        predictions = {}
        df = self.prepare_features(df)
        
        for item, model in self.models.items():
            item_predictions = []
            current_df = df[df['item_name'] == item].copy()
            
            for i in range(days_ahead):
                next_date = df['date'].max() + timedelta(days=i+1)
                
                # Prepare features for prediction
                pred_row = self._prepare_prediction_features(current_df, next_date, item)
                
                # Handle NaN values
                for column in pred_row.columns:
                    # Fill NaN with column mean, or 0 if all NaN
                    if pred_row[column].isna().any():
                        mean_val = pred_row[column].mean()
                        pred_row[column] = pred_row[column].fillna(
                            mean_val if not pd.isna(mean_val) else 0
                        )
                
                # Scale features
                pred_features_scaled = self.scalers[item].transform(pred_row)
                
                # Make prediction
                pred_qty = max(0, round(model.predict(pred_features_scaled)[0]))
                
                # Add prediction to results
                item_predictions.append({
                    'date': next_date.strftime('%Y-%m-%d'),  # Format date as string
                    'predicted_quantity': float(pred_qty)     # Convert to float
                })
                
                # Update current_df for next prediction
                new_row = current_df.iloc[-1:].copy()
                new_row['date'] = next_date
                new_row['quantity'] = pred_qty
                current_df = pd.concat([current_df, new_row])
            
            predictions[item] = item_predictions
        
        return predictions
    
    def _prepare_prediction_features(self, df, date, item):
        """Prepare features for a single prediction with NaN handling"""
        pred_features = pd.DataFrame({
            'date': [date],
            'item_name': [item],
            'quantity': [df['quantity'].iloc[-1]]
        })
        
        pred_features = self.prepare_features(pred_features)
        
        # Get group features if available
        group_features = self._get_group_features(
            item, 
            self._group_similar_items(df), 
            df
        )
        
        if group_features is not None:
            # Handle NaN in group features
            group_features = group_features.fillna(group_features.mean())
            group_features = group_features.fillna(0)  # Fill remaining NaN with 0
            
            return pd.concat([
                pred_features[self.feature_columns], 
                group_features
            ], axis=1)
        
        return pred_features[self.feature_columns]
        
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
    
    def _standardize_item_names(self, df):
        """Combine similar items by standardizing their names"""
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Mapping of similar items
        item_mapping = {
            # Classic items
            'Classic Combo': 'Classic',
            'Classic Burger': 'Classic',
            'Classic Meal Deal': 'Classic',
            'Classic Burger Combo': 'Classic',
            'Classic Burger Combo 1': 'Classic',
            'Classic Burger Combo 2': 'Classic',
            
            # Jazz items
            'Jazz Combo': 'Jazz',
            'Jazz Burger': 'Jazz',
            'Jazz Burger Combo': 'Jazz',
            'Jazz Meal Deal': 'Jazz',
            
            # Country items
            'Country Combo': 'Country',
            'Country Burger': 'Country',
            'Country Burger Combo': 'Country',
            'Country Meal Deal': 'Country',
            
            # Rock items
            'Rock Combo': 'Rock',
            'Rock Burger': 'Rock',
            'Rock Burger Combo': 'Rock',
            'Rock Meal Deal': 'Rock',
            
            # Family meals
            'Family Meal': 'Family Meal',
            'Family Meal 2.0': 'Family Meal',
            'Family Meal Deal': 'Family Meal'
        }
        
        # Replace item names
        df['item_name'] = df['item_name'].replace(item_mapping)
        
        # Combine quantities for same items on same date
        df = df.groupby(['date', 'item_name'], as_index=False).agg({
            'quantity': 'sum',
            'sales': 'sum'
        })
        
        print("\nUnique items after standardization:")
        for item in sorted(df['item_name'].unique()):
            count = len(df[df['item_name'] == item])
            print(f"{item}: {count} data points")
        
        return df 