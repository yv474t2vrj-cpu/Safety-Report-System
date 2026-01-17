from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "FLASK IS WORKING! Go to /dashboard for full app"

@app.route("/dashboard")
def dashboard():
    return "Dashboard will be here"

if __name__ == "__main__":
    print("Starting Flask on http://localhost:5000")
    app.run(debug=True, port=5000)
