from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO

# Create instances of extensions for SQLAlchemy and SocketIO
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///burgertone_inventory.db'
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")


# Funciton to create and configure the Flask app
def create_app():
    app = Flask(__name__)
    CORS(app) # Enable Cross-Origin Resource Sharing

    # LOad configurations
    app.config.from_object("config.Config")


    # Initialize the database
    db.init_app(app) # Bind SQLAlchemy to the Flask app
    socketio.init_app(app) # Bind SocketIO to the Flask app


    # Register Blueprints for routes
    from app.routes.ingredients import ingredients_blueprint
    app.register_blueprint(ingredients_blueprint, url_prefix="/ingredients")

    return app

# @app.route('/')
# def home():
#     return "Hello, Flask!"

# @app.route('/api/data')
# def get_data():
#     return {"data": "This is your data"}

# @app.route('/api/hello/<name>')
# def say_hello(name):
#     return {"message": f"Hello, {name}!"}


# if __name__ == '__main__':
#     app.run(debug=True)