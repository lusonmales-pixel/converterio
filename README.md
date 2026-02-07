# Convert — Мульти-конвертер файлов

Веб-приложение для конвертации файлов в различные форматы. Минималистичный дизайн в стиле SaaS.

## Технологический стек

- **Backend:** Python, Django (views без DRF)
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Конвертация:** Pillow, pydub, pdf2docx, python-docx, reportlab, xhtml2pdf, ffmpeg

## Поддерживаемые форматы

| Категория | Конвертации |
|-----------|-------------|
| **Изображения** | JPG↔PNG, JPG↔WEBP, PNG↔WEBP, PNG↔ICO, BMP→PNG, TIFF→JPG |
| **Аудио** | MP3↔WAV, MP3↔OGG, WAV→AAC, FLAC→MP3 |
| **Видео** | MP4↔WEBM, MOV→MP4, AVI→MP4 |
| **Документы** | PDF→DOCX, DOCX→PDF, TXT→PDF, TXT→DOCX, HTML→PDF |
| **Архивы** | ZIP↔TAR |

> **Примечание:** Для аудио и видео требуется [ffmpeg](https://ffmpeg.org/download.html) в системе (добавьте в PATH).

## Как запустить локально

### 1. Перейти в папку проекта

```bash
cd d:\www\file-converter
```

### 2. Создать виртуальное окружение (рекомендуется)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Применить миграции (опционально, для SQLite)

```bash
python manage.py migrate
```

> Если возникает ошибка о миграциях — можно пропустить, проект работает без БД для основной логики.

### 5. Запустить сервер

```bash
python manage.py runserver
```

Откройте в браузере: **http://127.0.0.1:8000**

## Структура проекта

```
file-converter/
├── config/              # Настройки Django
├── converter/           # Приложение конвертера
│   ├── converters/      # Модули конвертации по категориям
│   ├── formats.py       # Описание форматов и правил
│   └── views.py         # API endpoints
├── static/              # CSS, JS
├── templates/           # HTML
├── media/               # Временные файлы (создаётся автоматически)
├── manage.py
├── requirements.txt
└── README.md
```

## API

- `GET /` — главная страница
- `GET /api/detect/?filename=file.jpg` — определение формата и доступных целей
- `POST /api/convert/` — конвертация (form-data: `file`, `target`, `csrfmiddlewaretoken`)

## Ограничения

- Максимальный размер файла: 50 МБ (настраивается через `MAX_FILE_SIZE_MB`)

## Будущее развитие

Проект подготовлен к добавлению:

- Авторизация (Django auth)
- Лимиты конвертаций
- Платные тарифы

Как запустить
cd d:\www\file-converterpip install -r requirements.txtpython manage.py runserver
Откройте в браузере: http://127.0.0.1:800