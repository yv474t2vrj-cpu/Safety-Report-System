# Safety Report System - نظام تقارير السلامة
from flask import Flask, render_template, request, flash, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user 
from datetime import datetime
import os
import csv
import io
import webbrowser
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safety.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# جداول قاعدة البيانات
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    reporter = db.Column(db.String(100))
    status = db.Column(db.String(50), default='معلق')
    priority = db.Column(db.String(20), default='متوسط')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    """تهيئة قاعدة البيانات"""
    try:
        with app.app_context():
            db.create_all()
            
            # إنشاء مستخدم admin إذا لم يكن موجوداً
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@safety.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ تم إنشاء المستخدم الافتراضي")
                
    except Exception as e:
        print(f"⚠️ خطأ في قاعدة البيانات: {e}")
        # حاول إنشاء قاعدة بيانات جديدة
        try:
            if os.path.exists('safety.db'):
                os.remove('safety.db')
            with app.app_context():
                db.create_all()
                print("✅ تم إنشاء قاعدة بيانات جديدة")
        except Exception as e2:
            print(f"❌ خطأ حاد: {e2}")

# المسارات الأساسية
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    
    # إنشاء مجلد templates إذا لم يكن موجوداً
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # صفحة البداية الأصلية
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>نظام تقارير السلامة</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .container {
                max-width: 800px;
                width: 90%;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .status-box {
                background: #d4edda;
                color: #155724;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border: 2px solid #c3e6cb;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
            }
            .btn {
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 12px 25px;
                text-decoration: none;
                border-radius: 8px;
                margin: 10px;
                font-weight: bold;
            }
            .btn-success {
                background: #2ecc71;
            }
            .instructions {
                background: #fff8e1;
                padding: 20px;
                border-radius: 10px;
                margin-top: 30px;
                text-align: right;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="status-box">
                <h1>🚨 نظام تقارير السلامة</h1>
                <h2>Safety Report System</h2>
                <p>الإصدار الأصلي - يعمل مع Flask و SQLite</p>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>📝 تقارير السلامة</h3>
                    <p>إنشاء وإدارة تقارير السلامة</p>
                </div>
                <div class="feature">
                    <h3>👥 مستخدمين متعددين</h3>
                    <p>نظام تسجيل دخول آمن</p>
                </div>
                <div class="feature">
                    <h3>📊 تصدير البيانات</h3>
                    <p>تصدير التقارير بصيغة CSV</p>
                </div>
            </div>
            
            <div>
                <a href="/login" class="btn">🔐 تسجيل الدخول</a>
                <a href="/dashboard" class="btn btn-success">📊 لوحة التحكم</a>
            </div>
            
            <div class="instructions">
                <h3>👤 معلومات الدخول الافتراضية:</h3>
                <p>اسم المستخدم: <strong>admin</strong></p>
                <p>كلمة المرور: <strong>admin123</strong></p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect('/dashboard')
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>تسجيل الدخول</title>
        <style>
            body {
                font-family: Arial;
                background: #f5f5f5;
                padding: 50px;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .login-box {
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 400px;
            }
            h2 {
                text-align: center;
                color: #2c3e50;
                margin-bottom: 30px;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            }
            .alert {
                padding: 10px;
                border-radius: 5px;
                margin: 10px 0;
                text-align: center;
            }
            .success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>تسجيل الدخول</h2>
            
            <form method="POST">
                <input type="text" name="username" placeholder="اسم المستخدم" required>
                <input type="password" name="password" placeholder="كلمة المرور" required>
                <button type="submit">دخول</button>
            </form>
            
            <p style="text-align: center; margin-top: 20px;">
                <a href="/">العودة للصفحة الرئيسية</a>
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/dashboard')
@login_required
def dashboard():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    
    reports_html = ""
    for report in reports:
        status_color = {
            'معلق': '#3498db',
            'قيد المعالجة': '#f39c12',
            'مكتمل': '#2ecc71',
            'ملغي': '#e74c3c'
        }.get(report.status, '#7f8c8d')
        
        reports_html += f'''
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid {status_color};">
            <h3 style="margin: 0;">{report.title}</h3>
            <p style="color: #7f8c8d; margin: 5px 0;">الموقع: {report.location} | المبلغ: {report.reporter}</p>
            <p style="margin: 5px 0;">{report.description[:100]}...</p>
            <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                <span style="background: {status_color}; color: white; padding: 5px 10px; border-radius: 5px;">{report.status}</span>
                <span>{report.created_at.strftime("%Y-%m-%d %H:%M")}</span>
            </div>
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>لوحة التحكم</title>
        <style>
            body {{
                font-family: Arial;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }}
            .header {{
                background: #2c3e50;
                color: white;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: auto;
                padding: 20px;
            }}
            .btn {{
                background: #3498db;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 5px;
                display: inline-block;
            }}
            .btn-success {{
                background: #2ecc71;
            }}
            .btn-danger {{
                background: #e74c3c;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>لوحة التحكم</h1>
            <p>المستخدم: {current_user.username}</p>
        </div>
        <div class="container">
            <a href="/" class="btn">الرئيسية</a>
            <a href="/add_report" class="btn btn-success">إضافة تقرير</a>
            <a href="/export_reports" class="btn" style="background: #9b59b6;">تصدير CSV</a>
            <a href="/logout" class="btn btn-danger">تسجيل الخروج</a>
            
            <h2>التقارير ({len(reports)})</h2>
            {reports_html if reports else '<p style="text-align: center; padding: 40px;">لا توجد تقارير بعد</p>'}
        </div>
    </body>
    </html>
    '''

@app.route('/add_report', methods=['GET', 'POST'])
@login_required
def add_report():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        priority = request.form.get('priority', 'متوسط')
        
        new_report = Report(
            title=title,
            description=description,
            location=location,
            reporter=current_user.username,
            priority=priority,
            status='معلق'
        )
        
        db.session.add(new_report)
        db.session.commit()
        
        return '''
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>تم الإضافة</title>
            <style>
                body {
                    font-family: Arial;
                    padding: 50px;
                    text-align: center;
                }
                .success {
                    color: green;
                    font-size: 24px;
                }
            </style>
        </head>
        <body>
            <h1 class="success">تم إضافة التقرير بنجاح!</h1>
            <p><a href="/dashboard">العودة للوحة التحكم</a></p>
        </body>
        </html>
        '''
    
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>إضافة تقرير</title>
        <style>
            body {
                font-family: Arial;
                padding: 20px;
                background: #f5f5f5;
            }
            .form-container {
                max-width: 600px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            input, textarea, select {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            button {
                background: #2ecc71;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>إضافة تقرير جديد</h2>
            <form method="POST">
                <input type="text" name="title" placeholder="عنوان التقرير" required>
                <textarea name="description" placeholder="تفاصيل التقرير" rows="5" required></textarea>
                <input type="text" name="location" placeholder="الموقع" required>
                <select name="priority">
                    <option value="منخفض">منخفض</option>
                    <option value="متوسط" selected>متوسط</option>
                    <option value="عالي">عالي</option>
                </select>
                <button type="submit">إضافة التقرير</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">
                <a href="/dashboard">العودة للوحة التحكم</a>
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/export_reports')
@login_required
def export_reports():
    reports = Report.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # عنوان الملف
    writer.writerow(['ID', 'العنوان', 'الوصف', 'الموقع', 'المبلغ', 'الحالة', 'الأولوية', 'تاريخ الإنشاء'])
    
    # البيانات
    for report in reports:
        writer.writerow([
            report.id,
            report.title,
            report.description[:100] + '...' if len(report.description) > 100 else report.description,
            report.location,
            report.reporter,
            report.status,
            report.priority,
            report.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=تقارير_السلامة.csv"}
    )

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    print("=" * 70)
    print("🚨 نظام تقارير السلامة - النسخة الأصلية")
    print("=" * 70)
    print("✅ تم إصلاح مشكلة قاعدة البيانات")
    print("✅ نفس الواجهة الأصلية")
    print("✅ نفس التصميم الذي عملت عليه")
    print("=" * 70)
    print()
    print("🌐 رابط النظام:")
    print("   http://localhost:5000")
    print()
    print("👤 معلومات الدخول:")
    print("   اسم المستخدم: admin")
    print("   كلمة المرور: admin123")
    print()
    print("=" * 70)
    
    # تهيئة قاعدة البيانات
    init_db()
    
    # فتح المتصفح
    try:
        webbrowser.open("http://localhost:5000")
        print("🌐 جاري فتح المتصفح...")
    except:
        print("📱 افتح المتصفح يدوياً: http://localhost:5000")
    
    print()
    print("⚡ جاري تشغيل الخدمة...")
    print("🛑 لإيقاف: Ctrl+C")
    print("=" * 70)
    
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
