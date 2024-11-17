import os
from dotenv import load_dotenv



class Config:
    DATABASE_URI = os.getenv('DATABASE_URI',"sqlite:///burgertone_inventory.db")
    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids overhead

    # To load environment variables from a .env file into the os.environ dictionary
    load_dotenv()
    # Flask-SocketIO settings
    SOCKETIO_MESSAGE_QUEUE = os.getenv("REDIS_URL", "redis://")  # Optional, for scale-out