# Система аккаунтов — добавленные файлы

## Новое приложение `accounts`

```
accounts/
├── __init__.py
├── apps.py
├── forms.py          # RegistrationForm, LoginForm
├── views.py          # register_view, login_view, logout_view
├── urls.py           # /register/, /login/, /logout/
└── templates/accounts/
    ├── base_auth.html
    ├── login.html
    └── register.html
```

## Изменённые файлы (минимально)

### config/settings.py
- Добавлены в INSTALLED_APPS: `django.contrib.auth`, `django.contrib.sessions`, `accounts`
- Добавлены middleware: `SessionMiddleware`, `AuthenticationMiddleware`
- Добавлен context processor: `auth`
- Добавлены настройки: `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`, `AUTH_PASSWORD_VALIDATORS`

### config/urls.py
- Подключён `include('accounts.urls')`

### converter/views.py
- Добавлен декоратор `@login_required` к `index`, `detect_format`, `convert_file_view`

### templates/index.html
- В header добавлена навигация: username + Logout (если авторизован) или Login + Register

### static/styles.css
- Стили для `.header-inner`, `.auth-nav`, `.auth-link`, `.auth-user`

### static/auth.css (новый)
- Стили для форм входа и регистрации

## Поведение

- Неавторизованный пользователь при обращении к `/` или `/api/*` перенаправляется на `/login/`
- После успешной регистрации — автоматический вход и редирект на главную
- Вход возможен по username или email
- Выход — редирект на `/login/`
