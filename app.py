# -*- coding: utf-8 -*-
from flask import Flask, render_template, jsonify, request, flash, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user    
from datetime import datetime, timedelta
import os
import io
import csv
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'safety-dashboard-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/SAFETY/data/incidents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==================== DATABASE MODELS ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Pending')
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    date_resolved = db.Column(db.DateTime)
    reporter_name = db.Column(db.String(100))
    reporter_email = db.Column(db.String(100))
    location = db.Column(db.String(100))
    flight_number = db.Column(db.String(20))
    department = db.Column(db.String(50))
    assigned_to = db.Column(db.String(100))
    notes = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.incident_type,
            'severity': self.severity,
            'status': self.status,
            'date_reported': self.date_reported.strftime('%Y-%m-%d %H:%M'),
            'date_resolved': self.date_resolved.strftime('%Y-%m-%d %H:%M') if self.date_resolved else None,
            'reporter': self.reporter_name,
            'reporter_email': self.reporter_email,
            'location': self.location,
            'flight_number': self.flight_number,
            'department': self.department,
            'assigned_to': self.assigned_to,
            'notes': self.notes
        }

# ==================== LOGIN MANAGER ====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ROUTES ====================

@app.route('/')
@login_required
def home():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match', 'error')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_incident():
    if request.method == 'POST':
        incident = Incident(
            title=request.form.get('title'),
            description=request.form.get('description'),
            incident_type=request.form.get('type'),
            severity=request.form.get('severity'),
            reporter_name=current_user.username,
            reporter_email=current_user.email,
            location=request.form.get('location'),
            flight_number=request.form.get('flight_number'),
            department=request.form.get('department')
        )
        db.session.add(incident)
        db.session.commit()
        flash('Incident reported successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('report.html')

@app.route('/statistics')
@login_required
def statistics():
    stats = {
        'by_type': {'ground_ops': 1, 'maintenance': 2, 'medical': 1, 'safety': 1, 'security': 1},
        'by_severity': {'High': 3, 'Medium': 2, 'Low': 1},
        'total': 6
    }
    return render_template('statistics.html', stats=stats)




# ==================== API & EXPORT ROUTES ====================

@app.route('/api/stats')
@login_required
def get_stats():
    total = Incident.query.count()
    pending_count = Incident.query.filter_by(status='Pending').count()
    open_count = Incident.query.filter_by(status='Open').count()
    solved_count = Incident.query.filter_by(status='Solved').count()

    # Calculate percentages for chart
    incidents_by_type = db.session.query(
        Incident.incident_type,
        db.func.count(Incident.id)
    ).group_by(Incident.incident_type).all()

    incidents_by_severity = db.session.query(
        Incident.severity,
        db.func.count(Incident.id)
    ).group_by(Incident.severity).all()

    incidents_by_status = db.session.query(
        Incident.status,
        db.func.count(Incident.id)
    ).group_by(Incident.status).all()

    # Recent incidents (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_count = Incident.query.filter(Incident.date_reported >= week_ago).count()

    chart_data = {
        'types': dict(incidents_by_type),
        'severities': dict(incidents_by_severity),
        'statuses': dict(incidents_by_status),
        'recent_count': recent_count
    }

    return jsonify({
        'total': total,
        'pending': pending_count,
        'open': open_count,
        'solved': solved_count,
        'chart_data': chart_data
    })

@app.route('/api/incidents')
@login_required
def get_incidents():
    incidents = Incident.query.order_by(Incident.date_reported.desc()).all()
    return jsonify([inc.to_dict() for inc in incidents])

@app.route('/export/csv')
@login_required
def export_csv():
    incidents = Incident.query.all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(['ID', 'Title', 'Type', 'Severity', 'Status', 'Date Reported',
                     'Reporter', 'Location', 'Flight Number', 'Department', 'Assigned To'])

    for inc in incidents:
        writer.writerow([
            inc.id,
            inc.title,
            inc.incident_type,
            inc.severity,
            inc.status,
            inc.date_reported.strftime('%Y-%m-%d %H:%M'),
            inc.reporter_name,
            inc.location,
            inc.flight_number,
            inc.department,
            inc.assigned_to or 'Not assigned'
        ])

    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'safety_incidents_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@app.route('/export/html')
@login_required
def export_html():
    incidents = Incident.query.all()

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Safety Incidents Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ color: #0c2461; border-bottom: 3px solid #0c2461; padding-bottom: 10px; }}
            .header {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #0c2461; color: white; font-weight: bold; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            tr:hover {{ background-color: #f1f1f1; }}
            .badge {{ padding: 5px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; color: white; }}
            .badge-pending {{ background: #ffc107; color: #000; }}
            .badge-open {{ background: #fd7e14; color: #000; }}
            .badge-solved {{ background: #28a745; }}
            .badge-high {{ background: #dc3545; }}
            .badge-medium {{ background: #fd7e14; }}
            .badge-low {{ background: #20c997; }}
            .summary {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
            .summary-box {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); flex: 1; margin: 0 10px; text-align: center; }}
            .summary-box h3 {{ color: #0c2461; margin-bottom: 10px; }}
            .summary-value {{ font-size: 2em; font-weight: bold; color: #0c2461; }}
        </style>
    </head>
    <body>
        <h1>Safety Incidents Report</h1>

        <div class="header">
            <h2>Report Summary</h2>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>Reported by:</strong> {current_user.username}</p>
        </div>

        <div class="summary">
            <div class="summary-box">
                <h3>Total Incidents</h3>
                <div class="summary-value">{len(incidents)}</div>
            </div>
            <div class="summary-box">
                <h3>Pending</h3>
                <div class="summary-value">{sum(1 for inc in incidents if inc.status == 'Pending')}</div>    
            </div>
            <div class="summary-box">
                <h3>Solved</h3>
                <div class="summary-value">{sum(1 for inc in incidents if inc.status == 'Solved')}</div>            </div>
        </div>

        <h2>Incident Details</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Status</th>
                    <th>Date Reported</th>
                    <th>Reporter</th>
                    <th>Location</th>
                    <th>Department</th>
                </tr>
            </thead>
            <tbody>
    '''

    for inc in incidents:
        status_class = f'badge-{inc.status.lower()}'
        severity_class = f'badge-{inc.severity.lower()}'

        html += f'''
                <tr>
                    <td>{inc.id}</td>
                    <td><strong>{inc.title}</strong></td>
                    <td>{inc.incident_type}</td>
                    <td><span class="badge {severity_class}">{inc.severity}</span></td>
                    <td><span class="badge {status_class}">{inc.status}</span></td>
                    <td>{inc.date_reported.strftime('%Y-%m-%d %H:%M')}</td>
                    <td>{inc.reporter_name}</td>
                    <td>{inc.location}</td>
                    <td>{inc.department}</td>
                </tr>
        '''

    html += '''
            </tbody>
        </table>

        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">       
            <p><strong>Note:</strong> This is an automatically generated report from the Safety Dashboard 
System.</p>
            <p>For any questions, contact: safety-admin@company.com</p>
        </div>
    </body>
    </html>
    '''

    return html

@app.route('/incident/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_incident(id):
    incident = Incident.query.get_or_404(id)
    
    # Check if user has permission (admin or owner)
    if current_user.role != 'admin' and current_user.username != incident.reporter_name:
        flash('You do not have permission to edit this incident', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        incident.title = request.form.get('title')
        incident.description = request.form.get('description')
        incident.incident_type = request.form.get('type')
        incident.severity = request.form.get('severity')
        incident.location = request.form.get('location')
        incident.flight_number = request.form.get('flight_number')
        incident.department = request.form.get('department')
        
        db.session.commit()
        flash('Incident updated successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('edit_incident.html', incident=incident)

@app.route('/incident/<int:id>/delete', methods=['POST'])
@login_required
def delete_incident(id):
    incident = Incident.query.get_or_404(id)
    
    # Check if user has permission (admin or owner)
    if current_user.role != 'admin' and current_user.username != incident.reporter_name:
        flash('You do not have permission to delete this incident', 'error')
        return redirect(url_for('home'))
    
    db.session.delete(incident)
    db.session.commit()
    flash('Incident deleted successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        flash('Access denied. Admin only.', 'error')
        return redirect(url_for('home'))
    
    incidents = Incident.query.order_by(Incident.date_reported.desc()).all()
    return render_template('admin_panel.html', incidents=incidents)

@app.route('/incident/<int:id>/update-status', methods=['POST'])
@login_required
def update_incident_status(id):
    # Only admins can update status
    if current_user.role != 'admin':
        flash('Only administrators can update incident status', 'error')
        return redirect(url_for('home'))
    
    incident = Incident.query.get_or_404(id)
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    assigned_to = request.form.get('assigned_to', '')
    
    # Update incident
    incident.status = new_status
    incident.notes = notes
    incident.assigned_to = assigned_to
    
    # If status is "Solved", set resolved date
    if new_status == 'Solved':
        incident.date_resolved = datetime.utcnow()
    
    db.session.commit()
    flash(f'Incident status updated to {new_status}', 'success')
    return redirect(url_for('home'))
# ==================== INITIAL SETUP ====================

with app.app_context():
    os.makedirs('D:/SAFETY/data', exist_ok=True)
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@safety.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    print("=" * 60)
    print("SAFETY DASHBOARD")
    print("=" * 60)
    print("Features:")
    print("  * User Authentication & Registration")
    print("  * Incident Reporting Forms")
    print("  * Statistics Dashboard")
    print("  * Database Storage")
    print("")
    print("Default Admin Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("")
    print("Access from other devices:")
    print("  http://192.168.50.118:8000")
    print("")
    print("Press CTRL+C to stop")
    print("=" * 60)
    
    app.run(debug=True, port=8000, host='0.0.0.0')


