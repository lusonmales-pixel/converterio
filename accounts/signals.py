"""
Signals for accounts app.

Goal: PRO is granted automatically after registration (no payments).
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from plans.billing.services import get_pro_plan, assign_plan_to_user


@receiver(post_save, sender=User)
def assign_pro_plan(sender, instance: User, created: bool, **kwargs):
    if not created:
        return

    try:
        pro_plan = get_pro_plan()
        # PRO без срока действия (expires_at=None)
        assign_plan_to_user(instance, pro_plan, duration_days=0)
    except Exception:
        # Регистрация не должна ломаться из-за тарифов
        return

