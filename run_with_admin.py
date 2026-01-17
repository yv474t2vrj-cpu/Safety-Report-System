from app import app
from waitress import serve

if __name__ == '__main__':
    print("Starting Safety Dashboard on port 80...")
    print("Access from other devices: http://192.168.50.118")
    serve(app, host='0.0.0.0', port=80)