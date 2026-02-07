# Архитектура File Converter

## Обзор

Приложение построено по классической схеме Django: один основной экран, два API endpoint'а (detect, convert), чистая структура без DRF.

## Backend

### Структура

```
converter/
├── formats.py          # Единый источник форматов и правил конвертации
├── views.py            # HTTP-обработчики
└── converters/         # Модули конвертации
    ├── base.py         # ConversionError
    ├── images.py       # Pillow
    ├── audio.py        # pydub + ffmpeg
    ├── video.py        # ffmpeg
    ├── documents.py    # pdf2docx, python-docx, reportlab, xhtml2pdf
    └── archives.py     # zipfile, tarfile
```

### Поток данных

1. **Загрузка** — пользователь отправляет файл через `POST /api/convert/` (form-data).
2. **Валидация** — проверка размера, расширения, допустимости конвертации.
3. **Конвертация** — выбор конвертера по категории (formats.py → CONVERTERS), выполнение, возврат файла.
4. **Очистка** — удаление временных файлов в `finally`.

### Безопасность

- Валидация размера файла (MAX_FILE_SIZE_BYTES).
- Проверка допустимости пары форматов (CONVERSION_MATRIX).
- Автоудаление временных файлов.
- CSRF-защита для POST.

## Frontend

### Компоненты

- **Drop zone** — drag & drop и кнопка "Выбрать файл".
- **Conversion panel** — информация о файле, выбор целевого формата, прогресс, результат.
- **API** — `fetch` для detect, `XMLHttpRequest` для convert (progress upload).

### Поток

1. Пользователь выбирает/перетаскивает файл.
2. `GET /api/detect/?filename=...` → получение списка целевых форматов.
3. Выбор формата → активация кнопки "Конвертировать".
4. `POST /api/convert/` с progress → получение файла → кнопка "Скачать".

## Расширяемость

- **Новый формат:** добавить в `formats.py` (FORMATS, CONVERSION_MATRIX).
- **Новая конвертация:** реализовать функцию в соответствующем `converters/*.py`, подключить в `converters/__init__.py`.
- **Авторизация:** добавить `django.contrib.auth`, middleware, проверки в views.
- **Лимиты:** использовать `MAX_FILE_SIZE_MB` и новые настройки по тарифам.
