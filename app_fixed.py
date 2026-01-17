# Safety Report System - بدون pandas
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
import csv
import io
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/safety.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# نماذج قاعدة البيانات
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    reporter = db.Column(db.String(100))
    status = db.Column(db.String(50), default='جديد')
    priority = db.Column(db.String(20), default='متوسط')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# المسارات الرئيسية
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('dashboard.html', reports=reports)

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
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('تم تسجيل الخروج', 'info')
    return redirect('/')

@app.route('/add_report', methods=['GET', 'POST'])
@login_required
def add_report():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        location = request.form['location']
        priority = request.form['priority']
        
        new_report = Report(
            title=title,
            description=description,
            location=location,
            reporter=current_user.username,
            priority=priority
        )
        
        db.session.add(new_report)
        db.session.commit()
        flash('تم إضافة التقرير بنجاح!', 'success')
        return redirect('/dashboard')
    
    return render_template('add_report.html')

@app.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    report = Report.query.get_or_404(report_id)
    return render_template('view_report.html', report=report)

@app.route('/export_reports')
@login_required
def export_reports():
    reports = Report.query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # رأس الملف
    writer.writerow(['ID', 'العنوان', 'الموقع', 'المبلغ', 'الحالة', 'الأولوية', 'التاريخ'])
    
    # البيانات
    for report in reports:
        writer.writerow([
            report.id,
            report.title,
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
        headers={"Content-Disposition": "attachment;filename=reports.csv"}
    )

# صفحة بسيطة للتجربة
@app.route('/test')
def test_page():
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>اختبار النظام</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 50px; text-align: center; background: #f0f2f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
            .feature { background: #f8f9fa; padding: 20px; border-radius: 10px; }
            .btn { display: inline-block; background: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; margin: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ نظام تقارير السلامة - الإصدار المعدل</h1>
            <p>يعمل بدون pandas أو matplotlib</p>
            
            <div class="features">
                <div class="feature">
                    <h3>📝 تقارير</h3>
                    <p>إدارة تقارير السلامة</p>
                </div>
                <div class="feature">
                    <h3>👥 مستخدمين</h3>
                    <p>نظام تسجيل دخول آمن</p>
                </div>
                <div class="feature">
                    <h3>📊 تصدير</h3>
                    <p>تصدير البيانات لـ CSV</p>
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <a href="/login" class="btn">تسجيل الدخول</a>
                <a href="/dashboard" class="btn" style="background:#2ecc71;">لوحة التحكم</a>
            </div>
            
            <p style="margin-top: 30px; color: #7f8c8d;">
                🔗 <a href="http://localhost:5000">http://localhost:5000</a>
            </p>
        </div>
    </body>
    </html>
    '''

# إنشاء قاعدة البيانات عند التشغيل الأول
@app.before_first_request
def create_tables():
    db.create_all()
    # إنشاء مستخدم افتراضي إذا لم يكن موجوداً
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@safety.com',
            password_hash=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ تم إنشاء المستخدم الافتراضي: admin / admin123")

if __name__ == '__main__':
    print("=" * 70)
    print("🛡️  نظام تقارير السلامة - الإصدار المعدل")
    print("=" * 70)
    print("✅ يعمل بدون pandas أو matplotlib")
    print("🌐 افتح: http://localhost:5000")
    print("👤 المستخدم الافتراضي: admin / admin123")
    print("=" * 70)
    
    # إنشاء مجلد data إذا لم يكن موجوداً
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # إنشاء مجلد templates بسيط
    if not os.path.exists('templates'):
        os.makedirs('templates')
        # يمكنك إضافة قوالب HTML هنا لاحقاً
    
    app.run(host='0.0.0.0', port=5000, debug=True)
