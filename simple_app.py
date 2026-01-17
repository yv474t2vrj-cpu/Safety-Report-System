from flask import Flask, render_template_string

app = Flask(__name__)

# Simple HTML for dashboard
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Safety Dashboard</title>
    <style>
        body { font-family: Arial; background: #0c2461; color: white; padding: 20px; }
        .card { background: white; color: black; padding: 20px; margin: 10px; border-radius: 10px; }
        .metric { font-size: 40px; font-weight: bold; }
        button { background: red; color: white; padding: 15px; border: none; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>SAFETY OVERVIEW</h1>
    <div class="card">
        <h2>TOTAL INCIDENTS</h2>
        <div class="metric">5</div>
        <p>OPEN ISSUES: 3</p>
    </div>
    <div class="card">
        <h2>CRITICAL ALERTS</h2>
        <div class="metric">0</div>
        <p>RESOLVED: 2 (+12% vs last month)</p>
    </div>
    <button>Report Incident</button>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == '__main__':
    print("Open: http://localhost:5000")
    app.run(debug=True, port=5000)