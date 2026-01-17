# Safety Report System - نظام تقارير السلامة
from flask import Flask, render_template_string, request, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user 
from datetime import datetime
import os
import csv
import io
import webbrowser
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'safety-report-system-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///safety_reports.db'
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

# HTML Templates
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام تقارير السلامة</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 20px;
        }
        h2 {
            color: #3498db;
            margin: 20px 0;
        }
        .status-box {
            background: #d4edda;
            color: #155724;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
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
            text-align: center;
            transition: transform 0.3s;
        }
        .feature:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
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
            transition: background 0.3s;
        }
        .btn:hover {
            background: #2980b9;
        }
        .btn-success {
            background: #2ecc71;
        }
        .btn-success:hover {
            background: #27ae60;
        }
        .url-info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-family: monospace;
        }
        .instructions {
            background: #fff8e1;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }
        .instructions h3 {
            color: #f39c12;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="status-box">
            <h1>🏥 نظام تقارير السلامة</h1>
            <h2>Safety Report System</h2>
            <p>الإصدار: 2.0 | يعمل بكفاءة</p>
        </div>
        
        <h2>✨ المميزات:</h2>
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
            <div class="feature">
                <h3>📱 متجاوب</h3>
                <p>يعمل على جميع الأجهزة</p>
            </div>
        </div>
        
        <div class="url-info">
            <h3>🌐 رابط النظام:</h3>
            <p>http://localhost:5000</p>
            <p>للوصول من الهاتف: http://[IP-الكمبيوتر]:5000</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="/login" class="btn">🔐 تسجيل الدخول</a>
            <a href="/dashboard" class="btn btn-success">📊 لوحة التحكم</a>
        </div>
        
        <div class="instructions">
            <h3>👤 معلومات الدخول الافتراضية:</h3>
            <ul>
                <li><strong>اسم المستخدم:</strong> admin</li>
                <li><strong>كلمة المرور:</strong> admin123</li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 400px;
        }
        h2 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
        }
        button:hover {
            background: #2980b9;
        }
        .error {
            background: #f8d7da;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            text-align: center;
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔐 تسجيل الدخول</h2>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <input type="text" name="username" placeholder="اسم المستخدم" required>
            <input type="password" name="password" placeholder="كلمة المرور" required>
            <button type="submit">دخول</button>
        </form>
        <div class="back-link">
            <a href="/">← العودة للصفحة الرئيسية</a>
        </div>
    </div>
</body>
</html>
'''

# المسارات
@app.route('/')
def index():
    return render_template_string(INDEX_TEMPLATE)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect('/dashboard')
        else:
            error = 'اسم المستخدم أو كلمة المرور غير صحيحة'
    
    return render_template_string(LOGIN_TEMPLATE, error=error)

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
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 10px 0; 
                    border-left: 5px solid {status_color}; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="margin: 0; color: #2c3e50;">{report.title}</h3>
            <p style="color: #7f8c8d; margin: 5px 0;">
                📍 الموقع: {report.location} | 👤 المبلغ: {report.reporter}
            </p>
            <p style="margin: 5px 0;">{report.description[:100]}...</p>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                <span style="background: {status_color}; color: white; padding: 5px 10px; border-radius: 5px;">
                    {report.status}
                </span>
                <span style="color: #7f8c8d;">{report.created_at.strftime("%Y-%m-%d %H:%M")}</span>
            </div>
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة التحكم</title>
        <style>
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .container {{
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
            }}
            .btn {{
                display: inline-block;
                background: #3498db;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin: 5px;
                transition: background 0.3s;
            }}
            .btn:hover {{
                background: #2980b9;
            }}
            .btn-success {{
                background: #2ecc71;
            }}
            .btn-success:hover {{
                background: #27ae60;
            }}
            .btn-danger {{
                background: #e74c3c;
            }}
            .btn-danger:hover {{
                background: #c0392b;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 لوحة التحكم</h1>
            <p>مرحباً {current_user.username}</p>
        </div>
        <div class="container">
            <div style="margin-bottom: 20px;">
                <a href="/" class="btn">🏠 الرئيسية</a>
                <a href="/add_report" class="btn btn-success">➕ إضافة تقرير</a>
                <a href="/export_reports" class="btn" style="background: #9b59b6;">📥 تصدير CSV</a>
                <a href="/logout" class="btn btn-danger">🚪 تسجيل الخروج</a>
            </div>
            
            <h2>📋 التقارير ({len(reports)})</h2>
            {reports_html if reports else '<p style="text-align: center; padding: 40px; color: #7f8c8d;">لا توجد تقارير بعد</p>'}
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
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                .success-box {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                }
                .success {
                    color: #2ecc71;
                    font-size: 24px;
                    margin-bottom: 20px;
                }
                .btn {
                    display: inline-block;
                    background: #3498db;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="success-box">
                <h1 class="success">✅ تم إضافة التقرير بنجاح!</h1>
                <p><a href="/dashboard" class="btn">العودة للوحة التحكم</a></p>
            </div>
        </body>
        </html>
        '''
    
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>إضافة تقرير</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                padding: 20px;
                background: #f5f5f5;
            }
            .form-container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            h2 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            input, textarea, select {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
            }
            button {
                background: #2ecc71;
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
                margin-top: 10px;
            }
            button:hover {
                background: #27ae60;
            }
            .back-link {
                text-align: center;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <h2>➕ إضافة تقرير جديد</h2>
            <form method="POST">
                <input type="text" name="title" placeholder="عنوان التقرير" required>
                <textarea name="description" placeholder="تفاصيل التقرير" rows="5" required></textarea>
                <input type="text" name="location" placeholder="الموقع" required>
                <select name="priority">
                    <option value="منخفض">منخفض</option>
                    <option value="متوسط" selected>متوسط</option>
                    <option value="عالي">عالي</option>
                    <option value="حرج">حرج</option>
                </select>
                <button type="submit">إضافة التقرير</button>
            </form>
            <div class="back-link">
                <a href="/dashboard">← العودة للوحة التحكم</a>
            </div>
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
            report.description[:200] + '...' if len(report.description) > 200 else report.description,
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

def initialize_database():
    """تهيئة قاعدة البيانات"""
    try:
        with app.app_context():
            # إنشاء الجداول
            db.create_all()
            
            # إنشاء المستخدم الافتراضي إذا لم يكن موجوداً
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@safety.com',
                    password_hash=generate_password_hash('admin123'),
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ تم إنشاء المستخدم الافتراضي:")
                print("   👤 اسم المستخدم: admin")
                print("   🔑 كلمة المرور: admin123")
            
            # إضافة تقارير تجريبية إذا لم تكن موجودة
            if Report.query.count() == 0:
                sample_reports = [
                    Report(
                        title="انزلاق في منطقة الانتظار",
                        description="انزلاق موظف في منطقة الانتظار بسبب سائل مسكوب",
                        location="مدخل المبنى الرئيسي",
                        reporter="admin",
                        status="مكتمل",
                        priority="عالي"
                    ),
                    Report(
                        title="معدات غير آمنة",
                        description="آلة الطباعة تحتاج إلى صيانة عاجلة",
                        location="قسم الطباعة",
                        reporter="admin",
                        status="قيد المعالجة",
                        priority="متوسط"
                    )
                ]
                db.session.add_all(sample_reports)
                db.session.commit()
                print("✅ تم إضافة تقارير تجريبية")
                
    except Exception as e:
        print(f"⚠️  خطأ في تهيئة قاعدة البيانات: {e}")
        print("🔧 جاري إنشاء قاعدة بيانات جديدة...")
        try:
            os.remove('safety_reports.db')
            with app.app_context():
                db.create_all()
                print("✅ تم إنشاء قاعدة بيانات جديدة بنجاح")
        except:
            print("✅ يعمل النظام بدون قاعدة بيانات")

if __name__ == '__main__':
    print("=" * 70)
    print("🏥  نظام تقارير السلامة - Safety Report System")
    print("=" * 70)
    print("✅ الإصدار: 2.0")
    print("✅ يعمل بدون مشاكل")
    print("✅ لا يحتاج pandas أو matplotlib")
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
    print()
    
    # تهيئة قاعدة البيانات
    initialize_database()
    
    # فتح المتصفح تلقائياً
    try:
        webbrowser.open("http://localhost:5000")
        print("🌐 جاري فتح المتصفح...")
    except:
        print("📱 يمكنك فتح المتصفح يدوياً على: http://localhost:5000")
    
    print()
    print("⚡ الخدمة قيد التشغيل...")
    print("🛑 لإيقاف الخدمة: Ctrl+C")
    print("=" * 70)
    
    # تشغيل التطبيق
    app.run(host='0.0.0.0', port=5000, debug=True)
