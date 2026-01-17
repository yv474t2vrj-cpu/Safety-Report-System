from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head><meta charset="UTF-8"><title>نظام السلامة</title></head>
    <body>
        <h1>🚨 نظام تقارير السلامة يعمل!</h1>
        <p>افتح: <a href="http://localhost:5000/dashboard">لوحة التحكم</a></p>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head><meta charset="UTF-8"><title>لوحة التحكم</title></head>
    <body>
        <h1>📊 لوحة تحكم السلامة</h1>
        <p>النظام يعمل بنجاح!</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🌐 افتح: http://localhost:5000")
    app.run(debug=True)
