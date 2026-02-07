"""
Views для File Converter.
Обработка загрузки, определения формата и конвертации.
Регистрация не обязательна — гости имеют лимиты по тарифу FREE.
"""

import uuid
import shutil
from pathlib import Path

from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from django.shortcuts import render

from converter.formats import (
    normalize_format,
    get_available_targets,
    is_conversion_allowed,
    get_category,
)
from converter.converters import convert_file as do_convert
from converter.converters.base import ConversionError


@ensure_csrf_cookie
def index(request: HttpRequest) -> HttpResponse:
    """Главная страница с интерфейсом конвертера."""
    return render(request, 'index.html')


@require_GET
@ensure_csrf_cookie
def detect_format(request: HttpRequest) -> JsonResponse:
    """
    Определяет формат файла по расширению.
    Query: filename=example.jpg
    """
    filename = request.GET.get('filename', '')
    if not filename:
        return JsonResponse({'error': 'Не указано имя файла'}, status=400)

    ext = Path(filename).suffix.lstrip('.').lower()
    normalized = normalize_format(ext)
    if not normalized:
        return JsonResponse({
            'detected': None,
            'targets': [],
            'error': 'Формат не поддерживается',
        })

    targets = get_available_targets(ext)
    return JsonResponse({
        'detected': normalized,
        'targets': targets,
        'error': None,
    })


@require_POST
def convert_file_view(request: HttpRequest) -> JsonResponse | HttpResponse:
    """
    Принимает файл и целевой формат, конвертирует, возвращает файл или JSON с ошибкой.
    Проверка лимитов выполняется до конвертации.
    """
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'Файл не загружен'}, status=400)

    uploaded = request.FILES['file']
    target_ext = request.POST.get('target', '').strip().lower()
    source_ext = Path(uploaded.name).suffix.lstrip('.').lower()

    # Проверка целевого формата
    if not target_ext:
        return JsonResponse({'error': 'Не указан целевой формат'}, status=400)

    if not is_conversion_allowed(source_ext, target_ext):
        return JsonResponse({
            'error': f'Конвертация из {source_ext} в {target_ext} не поддерживается',
        }, status=400)

    # Проверка лимитов (количество, размер) — ДО конвертации
    from plans.utils import check_limits, increment_conversion_count
    from plans.utils import get_video_duration_seconds

    ok, err_msg, limit_exceeded = check_limits(request, uploaded.size, False, None)
    if not ok:
        return JsonResponse({
            'error': err_msg,
            'limit_exceeded': limit_exceeded,
        }, status=400)

    # Создаём временную папку для этой конвертации
    temp_id = str(uuid.uuid4())
    temp_dir = Path(settings.CONVERT_TEMP_DIR) / temp_id
    temp_dir.mkdir(parents=True, exist_ok=True)

    source_path = temp_dir / uploaded.name
    result_path = None

    try:
        # Сохраняем загруженный файл
        with open(source_path, 'wb') as f:
            for chunk in uploaded.chunks():
                f.write(chunk)

        # Проверка длительности видео (если применимо)
        is_video = get_category(normalize_format(source_ext) or source_ext) == 'video'
        video_duration = None
        if is_video:
            video_duration = get_video_duration_seconds(str(source_path))
            if video_duration is not None:
                ok, err_msg, limit_exceeded = check_limits(
                    request, uploaded.size, True, video_duration
                )
                if not ok:
                    return JsonResponse({
                        'error': err_msg,
                        'limit_exceeded': limit_exceeded,
                    }, status=400)

        # Конвертация (логика конвертера не изменена)
        result_path = do_convert(
            str(source_path),
            source_ext,
            target_ext,
            temp_dir,
        )

        if not result_path or not Path(result_path).exists():
            raise ConversionError('Результирующий файл не создан')

        # Успешная конвертация — увеличиваем счётчик
        increment_conversion_count(request)

        # Отдаём файл пользователю
        with open(result_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/octet-stream')
            out_name = Path(source_path).stem + '.' + target_ext
            response['Content-Disposition'] = f'attachment; filename="{out_name}"'
            return response

    except ConversionError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Ошибка сервера: {e}'}, status=500)
    finally:
        # Автоудаление временных файлов
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


# Убеждаемся, что CONVERT_TEMP_DIR создаётся при старте
def _ensure_temp_dir():
    p = Path(settings.CONVERT_TEMP_DIR)
    p.mkdir(parents=True, exist_ok=True)


# Вызов при импорте
_ensure_temp_dir()
