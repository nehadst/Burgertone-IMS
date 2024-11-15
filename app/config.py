import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("mysql+pymysql://username:password@localhost:3306/burgertone_inventory")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids overhead


    # Flask-SocketIO settings
    SOCKETIO_MESSAGE_QUEUE = os.getenv("REDIS_URL", "redis://")  # Optional, for scale-out