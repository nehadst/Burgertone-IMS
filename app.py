from flask import Flask

app = Flask(__name__)
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