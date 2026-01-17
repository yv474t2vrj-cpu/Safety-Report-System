#!/usr/bin/env python3
"""
تشغيل تطبيق Flask للوصول من جميع الأجهزة
"""

import sys
import os
import socket
import webbrowser
from datetime import datetime

# إضافة المسار الحالي
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    
    def get_ip_address():
        """الحصول على عناوين IP للجهاز"""
        ips = []
        try:
            # الحصول على اسم الجهاز
            hostname = socket.gethostname()
            
            # الحصول على جميع عناوين IP
            all_ips = socket.gethostbyname_ex(hostname)[2]
            
            # تصفية عناوين localhost
            for ip in all_ips:
                if not ip.startswith('127.'):
                    ips.append(ip)
                    
            # إذا لم نجد عناوين، نستخدم طريقة بديلة
            if not ips:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ips.append(s.getsockname()[0])
                s.close()
                
        except Exception as e:
            ips.append("127.0.0.1")
            
        return ips
    
    def print_network_info():
        """طباعة معلومات الشبكة"""
        print("=" * 60)
        print("🛡️  نظام تقارير السلامة - Safety Report System")
        print("=" * 60)
        
        ips = get_ip_address()
        
        print("\n📡 يمكن الوصول للتطبيق من:")
        print("-" * 40)
        
        # العنوان المحلي
        print("📍 على هذا الجهاز:")
        print(f"   http://localhost:5000")
        print(f"   http://127.0.0.1:5000")
        
        # عناوين الشبكة
        if len(ips) > 0:
            print(f"\n📱 من الأجهزة الأخرى على نفس الشبكة:")
            for ip in ips:
                print(f"   http://{ip}:5000")
        
        print("\n🔗 روابط سريعة:")
        for ip in ips:
            print(f"   http://{ip}:5000/dashboard")
            print(f"   http://{ip}:5000/reports")
        
        print("\n⏰ وقت البدء:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("=" * 60)
        print("\n📝 اضغط Ctrl+C لإيقاف الخادم\n")
    
    if __name__ == '__main__':
        # عرض معلومات الشبكة
        print_network_info()
        
        # محاولة فتح المتصفح تلقائياً
        try:
            webbrowser.open("http://localhost:5000")
        except:
            pass
        
        # تشغيل التطبيق
        app.run(
            host='0.0.0.0',    # الاستماع على جميع الواجهات
            port=5000,         # المنفذ
            debug=True,        # وضع التصحيح
            threaded=True,     # دعم مستخدمين متعددين
            use_reloader=True  # إعادة التحميل التلقائي عند التعديل
        )

except ImportError as e:
    print(f"❌ خطأ: {e}")
    print("تأكد من:")
    print("1. وجود ملف app.py في نفس المجلد")
    print("2. تثبيت Flask: pip install flask")
    print("3. تفعيل virtual environment: .venv\Scripts\activate")
    input("\nاضغط Enter للخروج...")
