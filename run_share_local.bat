@echo off
REM Запуск для доступа с других устройств в локальной сети (тот же Wi-Fi / кабель)
REM Сервер слушает 0.0.0.0:8000

echo.
echo  Local network sharing — other devices can open:
echo  http://ВАШ_IP:8000
echo  (Узнать IP: в другом окне выполните  ipconfig  и смотрите "IPv4")
echo.
echo  On this PC: http://127.0.0.1:8000/
echo.

python manage.py runserver 0.0.0.0:8000
