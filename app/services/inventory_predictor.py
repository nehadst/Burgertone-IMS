from sklearn.linear_regression import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import openai

class InventoryPredictor:
    def __init__(self):
        self.model = RandomForestRegressor()
        self.openai = openai.OpenAI()
        
    def train_model(self, X, y):
        """Train ML model on historical data"""
        self.model.fit(X, y)
        
    def get_ai_insights(self, predictions, actual):
        """Get OpenAI analysis of predictions"""
        prompt = f"""
        Analyze these inventory predictions:
        Predicted: {predictions}
        Actual: {actual}
        
        Provide insights on:
        1. Accuracy
        2. Potential factors affecting demand
        3. Recommendations for inventory levels
        """
        
        response = self.openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content 