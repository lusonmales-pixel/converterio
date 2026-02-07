"""
Billing-сервис для работы с тарифами пользователей.
Конвертер не знает, как работают тарифы — он только спрашивает лимиты.
"""

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User

from plans.models import Plan, UserPlan


def get_free_plan() -> Plan:
    """Получает или создаёт FREE тариф."""
    plan, _ = Plan.objects.get_or_create(
        name=Plan.FREE,
        defaults={
            'price_rub': 0,
            'duration_days': 0,
            'limits': {
                'conversions_per_day': 3,
                'max_file_size_mb': 25,
                'available_formats': 'all',  # Все форматы доступны
            }
        }
    )
    return plan


def get_pro_plan() -> Plan:
    """Получает или создаёт PRO тариф."""
    plan, _ = Plan.objects.get_or_create(
        name=Plan.PRO,
        defaults={
            'price_rub': 0,
            'duration_days': 0,
            'limits': {
                # Лимиты оставляем как структуру для будущего расширения,
                # но фактически конвертер сейчас работает без ограничений.
                'conversions_per_day': 999999,
                'max_file_size_mb': 999999,
                'available_formats': 'all',
            }
        }
    )
    return plan


def get_user_plan(user: User | None) -> Plan:
    """
    Возвращает текущий активный тариф пользователя.
    Если пользователь не авторизован или нет активного тарифа → FREE.
    """
    if not user or not user.is_authenticated:
        return get_free_plan()

    # Проверяем активные тарифы
    active_plans = UserPlan.objects.filter(
        user=user,
        is_active=True
    ).select_related('plan').order_by('-started_at')

    for user_plan in active_plans:
        # Проверяем, не истёк ли тариф
        if not user_plan.check_expired():
            return user_plan.plan

    # Если активных тарифов нет → FREE
    return get_free_plan()


def user_has_active_plan(user: User | None, plan_name: str) -> bool:
    """
    Проверяет, есть ли у пользователя активный тариф с указанным именем.
    """
    if not user or not user.is_authenticated:
        return plan_name == Plan.FREE

    current_plan = get_user_plan(user)
    return current_plan.name == plan_name


def assign_plan_to_user(user: User, plan: Plan, duration_days: int | None = None) -> UserPlan:
    """
    Назначает тариф пользователю.
    Если тариф платный, создаёт UserPlan с expires_at.
    Для FREE создаёт UserPlan без expires_at.
    """
    if not user.is_authenticated:
        raise ValueError("Пользователь должен быть авторизован")

    # Деактивируем старые тарифы
    UserPlan.objects.filter(user=user, is_active=True).update(is_active=False)

    # Определяем срок действия
    expires_at = None
    if plan.name != Plan.FREE:
        if duration_days is None:
            duration_days = plan.duration_days
        if duration_days > 0:
            expires_at = timezone.now() + timedelta(days=duration_days)

    # Создаём новый UserPlan
    user_plan = UserPlan.objects.create(
        user=user,
        plan=plan,
        started_at=timezone.now(),
        expires_at=expires_at,
        is_active=True,
    )

    return user_plan


def expire_old_user_plans():
    """
    Деактивирует истёкшие тарифы пользователей.
    Должна вызываться периодически (например, через cron или celery).
    """
    now = timezone.now()
    expired_count = UserPlan.objects.filter(
        is_active=True,
        expires_at__lt=now
    ).exclude(plan__name=Plan.FREE).update(is_active=False)

    return expired_count
