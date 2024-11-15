from flask import Flask

app = Flask(__name__)

def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(debug=true)