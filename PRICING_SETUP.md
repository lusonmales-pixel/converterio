# Тарифы и лимиты

## Добавленные компоненты

### Приложение `plans`
- `models.py` — Plan, UserProfile, DailyUsage
- `limits_config.py` — конфигурация лимитов (FREE, BASIC, PRO)
- `utils.py` — проверка лимитов, счётчики, видео-длительность
- `views.py` — страница /pricing/
- `management/commands/init_plans.py` — инициализация тарифов в БД

### Изменения
- **converter/views.py** — снят @login_required, добавлена проверка лимитов до конвертации
- **accounts/views.py** — создание UserProfile с тарифом BASIC при регистрации
- **config/settings.py** — plans в INSTALLED_APPS, LOGOUT_REDIRECT_URL = '/'
- **templates/index.html** — ссылка «Тарифы», модальное окно при достижении лимита
- **static/main.js** — обработка limit_exceeded, показ модального окна

## Тарифы

| Тариф | Конвертаций/день | Размер файла | Видео | Доступ |
|-------|------------------|--------------|-------|--------|
| **Free** (гость) | 3 | 25 МБ | до 30 сек | Всегда |
| **Basic** (аккаунт) | 20 | 200 МБ | до 3 мин | Регистрация |
| **Pro** | 100 | 1 ГБ | без ограничения | Скоро |

## Первый запуск
```bash
python manage.py migrate
python manage.py init_plans
```
