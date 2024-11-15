from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///burgertone_inventory.db'
db = SQLAlchemy(app)

class Ingredients(db.Model):
    id = db.Column(d.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    unit = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Float(10,2), nullable=False)
    threshold = db.Column(db.Float(10,2), nullable=False)

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