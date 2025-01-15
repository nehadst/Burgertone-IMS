
from app.models.ingredient import Ingredients
from flask import current_app


#This function will handle sending low stock alerts to connected clients


def send_low_stock_alert(socketio):
    with current_app.app_context():  # Ensure app context is active
        low_stock_items = Ingredients.query.filter(
            Ingredients.quantity <= Ingredients.threshold
        ).all()

        if low_stock_items:
            alert_data = [item.to_dict() for item in low_stock_items]
            socketio.emit("LOW_STOCK_ALERT", {"items": alert_data}, broadcast=True)