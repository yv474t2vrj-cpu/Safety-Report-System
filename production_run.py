from waitress import serve
from app import app
import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    ip = get_ip()
    print("=" * 60)
    print("🏢 SAFETY DASHBOARD - PRODUCTION MODE")
    print("=" * 60)
    print(f"Server running on: http://{ip}:80")
    print(f"Access from other devices: http://{ip}")
    print("=" * 60)
    
    # Serve on all interfaces, port 80
    serve(app, host='0.0.0.0', port=80)