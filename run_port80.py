from app import app
import socket

# Get local IP address
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    ip = get_ip()
    print("=" * 60)
    print("🚀 SAFETY DASHBOARD - PORT 80")
    print("=" * 60)
    print(f"Local:    http://localhost")
    print(f"Network:  http://{ip}")
    print(f"Your IP:  {ip}")
    print("=" * 60)
    print("📱 Access from other devices:")
    print(f"http://{ip}")
    print("=" * 60)
    
    # Try port 80, if fails try 8000
    try:
        app.run(debug=True, port=80, host='0.0.0.0')
    except PermissionError:
        print("Port 80 requires Admin. Falling back to port 8000...")
        print(f"Access from other devices: http://{ip}:8000")
        app.run(debug=True, port=8000, host='0.0.0.0')