from flask_socketio import emit
from app.models.ingredient import Ingredients


#This function will handle sending low stock alerts
#to connected clients


def send_low_stock_alert(socketio):
    from app import db
    with db.session() as session:
        low_stock_items = session.query(Ingredients).filter(Ingredients.quality <= Ingredients.threshold).all()
        if low_stock_items:
            alert_data = [item.to_dict() for item in low_stock_items]
            socketio.emit("LOW_STOCK_ALERT", {"items": alert_data}, broadcast=True)