@echo off
echo Setting up port forwarding...
echo Port 80 -> Port 8000
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run as Administrator!
    echo Right-click -> Run as Administrator
    pause
    exit /b 1
)

REM Add port forwarding rule
netsh interface portproxy add v4tov4 listenport=80 listenaddress=0.0.0.0 connectport=8000 connectaddress=127.0.0.1

echo Port forwarding configured!
echo.
echo Now run Flask on port 8000:
echo python app.py
echo.
echo Access from other devices: http://YOUR-IP
pause