from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Burgertone Inventory API"}

def test_get_predictions():
    response = client.get("/api/inventory/predictions/7")
    assert response.status_code == 200
    predictions = response.json()
    assert len(predictions) > 0
    assert "item_name" in predictions[0]
    assert "predictions" in predictions[0]

def test_get_historical_data():
    # First get list of items
    items_response = client.get("/api/inventory/items")
    assert items_response.status_code == 200
    items = items_response.json()["items"]
    
    # Test historical data for first item
    if items:
        response = client.get(f"/api/inventory/historical/{items[0]}")
        assert response.status_code == 200
        data = response.json()
        assert "dates" in data
        assert "quantities" in data
        assert "sales" in data

def test_get_insights():
    # First get list of items
    items_response = client.get("/api/inventory/items")
    assert items_response.status_code == 200
    items = items_response.json()["items"]
    
    # Test insights for first item
    if items:
        response = client.get(f"/api/inventory/insights/{items[0]}")
        assert response.status_code == 200
        assert "insights" in response.json() 