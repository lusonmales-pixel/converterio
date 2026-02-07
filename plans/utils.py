"""
Утилиты проверки лимитов.
Проверка выполняется ПЕРЕД конвертацией, без изменения логики конвертера.
Конвертер не знает, как работают тарифы — он только спрашивает лимиты.
"""

import subprocess
from datetime import date
from pathlib import Path

from django.utils import timezone

from .billing.services import get_user_plan


def get_video_duration_seconds(file_path: str) -> float | None:
    """Получает длительность видео в секундах через ffprobe. None если не видео или ошибка."""
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', str(file_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass
    return None


def get_limits_for_request(request) -> dict:
    """
    Возвращает лимиты для текущего пользователя/гостя.
    Использует billing/services для определения тарифа.
    """
    user = request.user if request.user.is_authenticated else None
    plan = get_user_plan(user)

    # Получаем лимиты из JSONField
    limits = plan.limits if plan.limits else {}
    if not limits:
        # Fallback на дефолтные значения
        limits = {
            'conversions_per_day': 3,
            'max_file_size_mb': 25,
            'available_formats': 'all',
        }

    max_file_size_mb = limits.get('max_file_size_mb', 25)
    max_video_seconds = limits.get('max_video_seconds', 30)
    if max_video_seconds == 0:
        max_video_seconds = 999999

    return {
        'conversions_per_day': limits.get('conversions_per_day', 3),
        'max_file_size_bytes': max_file_size_mb * 1024 * 1024,
        'max_video_seconds': max_video_seconds,
        'plan_code': plan.name.lower(),
    }


def get_today_conversion_count(request) -> int:
    """Количество конвертаций сегодня для пользователя или гостя."""
    if request.user.is_authenticated:
        from .models import DailyUsage
        today = timezone.localdate()
        try:
            usage = DailyUsage.objects.get(user=request.user, date=today)
            return usage.count
        except DailyUsage.DoesNotExist:
            return 0
    else:
        # Гость: session
        session = request.session
        today_str = str(date.today())
        if session.get('usage_date') != today_str:
            return 0
        return session.get('usage_count', 0)


def increment_conversion_count(request) -> None:
    """Увеличивает счётчик конвертаций после успешной конвертации."""
    if request.user.is_authenticated:
        from .models import DailyUsage
        today = timezone.localdate()
        usage, _ = DailyUsage.objects.get_or_create(
            user=request.user,
            date=today,
            defaults={'count': 0},
        )
        usage.count += 1
        usage.save()
    else:
        session = request.session
        today_str = str(date.today())
        if session.get('usage_date') != today_str:
            session['usage_date'] = today_str
            session['usage_count'] = 0
        session['usage_count'] = session.get('usage_count', 0) + 1
        session.modified = True


def check_limits(
    request,
    file_size: int,
    is_video: bool,
    video_duration_seconds: float | None = None,
) -> tuple[bool, str, bool]:
    """
    Проверяет лимиты перед конвертацией.
    Возвращает (ok, error_message, limit_exceeded).
    limit_exceeded=True означает, что показать "Зарегистрироваться / Тарифы".
    """
    # В упрощённой тарифной системе лимиты отключены:
    # конвертер работает для всех без ограничений.
    return True, '', False

    limits = get_limits_for_request(request)
    count = get_today_conversion_count(request)

    if count >= limits['conversions_per_day']:
        plan_name = limits.get('plan_code', 'free')
        if plan_name == 'free':
            message = (
                f'Достигнут лимит конвертаций на сегодня ({limits["conversions_per_day"]}). '
                'Перейдите на PRO для расширенных лимитов.'
            )
        else:
            message = (
                f'Достигнут лимит конвертаций на сегодня ({limits["conversions_per_day"]}). '
                'Перейдите на PRO для расширенных лимитов.'
            )
        return False, message, True

    if file_size > limits['max_file_size_bytes']:
        max_mb = limits['max_file_size_bytes'] // (1024 * 1024)
        return False, (
            f'Файл слишком большой. Максимум для вашего тарифа: {max_mb} МБ. '
            'Перейдите на PRO для больших файлов.'
        ), True

    if is_video and video_duration_seconds is not None:
        max_sec = limits['max_video_seconds']
        if max_sec > 0 and max_sec < 999999 and video_duration_seconds > max_sec:
            return False, (
                f'Видео слишком длинное. Максимум: {max_sec} сек. '
                'Перейдите на PRO для видео без ограничений.'
            ), True

    return True, '', False
