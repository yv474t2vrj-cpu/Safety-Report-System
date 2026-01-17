from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "FLASK IS WORKING!"

if __name__ == '__main__':
    print("Starting server at http://localhost:5000")
    app.run(debug=True, port=5000)