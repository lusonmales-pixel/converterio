# Деплой Django File Converter на Railway / Render / Fly.io

## Требуемые Environment Variables

### Обязательные

```bash
# Django Secret Key (обязательно!)
DJANGO_SECRET_KEY=your-super-secret-key-here-min-50-chars

# Debug режим (для продакшена = False)
DEBUG=False

# Allowed hosts (через запятую, без пробелов)
# Для Railway: ваш-проект.railway.app
# Для Render: ваш-проект.onrender.com
# Для Fly.io: ваш-проект.fly.dev
ALLOWED_HOSTS=your-domain.com,*.railway.app,*.onrender.com,*.fly.dev

# Database (если используете внешнюю БД)
# Для SQLite (по умолчанию) - ничего не нужно
# Для PostgreSQL:
DATABASE_URL=postgresql://user:password@host:port/dbname
# Или отдельно:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

### Опциональные

```bash
# Максимальный размер файла (МБ)
MAX_FILE_SIZE_MB=50

# Billing (если используется)
PAYMENTS_ENABLED=True
PAYMENT_PROVIDER=mock
```

## Деплой на Railway

### 1. Подготовка

1. Убедитесь, что `Dockerfile` и `.dockerignore` находятся в корне репозитория
2. Закоммитьте изменения в Git

### 2. Создание проекта на Railway

1. Зайдите на [railway.app](https://railway.app)
2. Нажмите "New Project" → "Deploy from GitHub repo"
3. Выберите ваш репозиторий
4. Railway автоматически обнаружит Dockerfile

### 3. Настройка Environment Variables

В настройках проекта Railway добавьте:

```
DJANGO_SECRET_KEY=<сгенерируйте через: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=*.railway.app
```

### 4. Настройка базы данных (опционально)

Если нужна PostgreSQL:
1. В Railway добавьте PostgreSQL service
2. Railway автоматически создаст `DATABASE_URL`
3. Обновите `settings.py` для использования `DATABASE_URL` (если нужно)

### 5. Деплой

Railway автоматически:
- Соберёт Docker образ
- Запустит контейнер
- Присвоит домен (например: `your-project.railway.app`)

### 6. Первоначальная настройка БД

После первого деплоя выполните миграции:

```bash
# Через Railway CLI или в настройках проекта → "Deploy Logs" → "Run Command"
railway run python manage.py migrate
railway run python manage.py init_plans
```

Или добавьте в `Dockerfile` перед CMD (если хотите автоматически):

```dockerfile
# В Dockerfile перед CMD добавьте:
RUN python manage.py migrate --noinput || true
RUN python manage.py init_plans || true
```

## Деплой на Render

### 1. Подготовка

Аналогично Railway - убедитесь, что Dockerfile в корне.

### 2. Создание Web Service

1. Зайдите на [render.com](https://render.com)
2. "New" → "Web Service"
3. Подключите GitHub репозиторий
4. Выберите:
   - **Build Command**: `docker build -t file-converter .`
   - **Start Command**: `docker run -p $PORT:8000 file-converter`
   - Или используйте "Docker" как тип сервиса

### 3. Environment Variables

В разделе "Environment" добавьте те же переменные, что и для Railway.

### 4. Деплой

Render автоматически соберёт и запустит контейнер.

## Деплой на Fly.io

### 1. Установка Fly CLI

```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Mac/Linux
curl -L https://fly.io/install.sh | sh
```

### 2. Логин и создание приложения

```bash
fly auth login
fly launch
```

### 3. Настройка fly.toml (опционально)

Fly.io может создать `fly.toml` автоматически, но можно настроить:

```toml
app = "your-app-name"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  DJANGO_SECRET_KEY = "your-secret-key"
  DEBUG = "False"
  ALLOWED_HOSTS = "*.fly.dev"

[[services]]
  internal_port = 8000
  protocol = "tcp"
```

### 4. Деплой

```bash
fly deploy
```

## Проверка работоспособности

После деплоя проверьте:

1. Главная страница: `https://your-domain.com/`
2. Страница тарифов: `https://your-domain.com/pricing/`
3. API конвертации: `https://your-domain.com/api/convert/`

## Troubleshooting

### Ошибка: "DisallowedHost"

Убедитесь, что `ALLOWED_HOSTS` содержит ваш домен.

### Ошибка: "Static files not found"

Dockerfile автоматически собирает статику через `collectstatic`. Если проблемы:
- Проверьте, что `STATIC_ROOT` настроен в `settings.py`
- Убедитесь, что `STATICFILES_DIRS` содержит правильные пути

### Ошибка: "Database locked" (SQLite)

SQLite не подходит для продакшена с несколькими воркерами. Используйте PostgreSQL:
- Railway: добавьте PostgreSQL service
- Render: добавьте PostgreSQL database
- Fly.io: используйте внешний PostgreSQL или Fly Postgres

### FFmpeg не работает

Убедитесь, что в Dockerfile установлен `ffmpeg` (уже добавлен).

## Рекомендации для продакшена

1. **Используйте PostgreSQL** вместо SQLite для продакшена
2. **Настройте логирование** (Django logging в `settings.py`)
3. **Добавьте мониторинг** (Sentry, DataDog и т.д.)
4. **Настройте бэкапы БД** (если используете внешнюю БД)
5. **Ограничьте размер загружаемых файлов** через `MAX_FILE_SIZE_MB`
6. **Настройте CDN** для статики (если нужно)
