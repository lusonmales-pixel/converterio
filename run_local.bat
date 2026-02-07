@echo off
REM Локальный запуск: без переменных окружения (DEBUG=True, localhost в ALLOWED_HOSTS)
echo Starting Django at http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000
