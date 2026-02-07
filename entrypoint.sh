#!/bin/bash
set -e

# Выполняем миграции
echo "Running migrations..."
python manage.py migrate --noinput

# Инициализируем тарифы (если нужно)
echo "Initializing plans..."
python manage.py init_plans || true

# Запускаем Gunicorn
echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 --access-logfile - --error-logfile - config.wsgi:application
