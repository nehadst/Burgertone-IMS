from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///burgertone_inventory.db'
db = SQLAlchemy(app)

@app.route('/')
def home():
    return "Hello, Flask!"

@app.route('/api/data')
def get_data():
    return {"data": "This is your data"}

@app.route('/api/hello/<name>')
def say_hello(name):
    return {"message": f"Hello, {name}!"}


if __name__ == '__main__':
    app.run(debug=True)