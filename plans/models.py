"""
Модели тарифов и использования.
Подготовлено к будущим платежам.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Plan(models.Model):
    """Тарифный план."""
    FREE = 'FREE'
    PRO = 'PRO'

    NAME_CHOICES = [
        (FREE, 'Free'),
        (PRO, 'Pro'),
    ]

    name = models.CharField(max_length=20, unique=True, choices=NAME_CHOICES)
    price_rub = models.IntegerField(default=0, help_text='Цена в рублях')
    duration_days = models.IntegerField(default=0, help_text='Длительность в днях (0 для FREE)')
    limits = models.JSONField(
        default=dict,
        help_text='Лимиты: conversions_per_day, max_file_size_mb, available_formats'
    )

    class Meta:
        ordering = ['price_rub']

    def __str__(self):
        return self.name

    def get_limit(self, key, default=None):
        """Получить значение лимита."""
        return self.limits.get(key, default)


class UserPlan(models.Model):
    """Активный тариф пользователя."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_plans',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='user_plans',
    )
    started_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True, help_text='None для FREE')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.user.username} — {self.plan.name} ({self.started_at.date()})'

    def check_expired(self):
        """Проверяет, истёк ли тариф."""
        if self.plan.name == Plan.FREE:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            self.is_active = False
            self.save(update_fields=['is_active'])
            return True
        return False


class Payment(models.Model):
    """Платёж (mock или реальный)."""
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Ошибка'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.PROTECT,
        related_name='payments',
    )
    amount = models.IntegerField(help_text='Сумма в рублях')
    currency = models.CharField(max_length=3, default='RUB')
    provider = models.CharField(max_length=50, default='mock', help_text='Провайдер платежа')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    external_payment_id = models.CharField(max_length=255, blank=True, help_text='ID платежа у провайдера')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} — {self.plan.name} — {self.amount} RUB ({self.status})'


# Обратная совместимость: оставляем DailyUsage
class DailyUsage(models.Model):
    """Дневной счётчик конвертаций пользователя."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_usage',
    )
    date = models.DateField(db_index=True)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['user', 'date']

    def __str__(self):
        return f'{self.user.username} — {self.date}: {self.count}'
