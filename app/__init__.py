from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
socketio = SocketIO(async_mode="eventlet", cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Load configurations
    app.config.from_object("app.config.Config")

    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)

    # Register Blueprints
    from app.routes.ingredients import ingredients_blueprint
    app.register_blueprint(ingredients_blueprint, url_prefix="/ingredients")

    # Import here to avoid circular import
    from app.websocket.alert_service import send_low_stock_alert

    # Register after_request handler
    @app.after_request
    def check_inventory_levels(response):
        send_low_stock_alert(socketio)
        return response

    return app