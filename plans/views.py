"""Views для страницы тарифов."""

from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import Plan
from .billing.services import get_user_plan, user_has_active_plan, get_free_plan, get_pro_plan


@require_GET
@ensure_csrf_cookie
def pricing_view(request):
    """Страница сравнения тарифов."""
    # Получаем текущий тариф пользователя
    current_plan = get_user_plan(request.user if request.user.is_authenticated else None)
    is_pro_active = user_has_active_plan(request.user if request.user.is_authenticated else None, Plan.PRO)

    free_plan = get_free_plan()
    pro_plan = get_pro_plan()

    # Формируем данные для шаблона
    plans_data = []

    # FREE тариф
    free_data = {
        'name': free_plan.name,
        'limits': free_plan.limits or {},
        'is_pro_plan': False,
    }
    if current_plan.name == Plan.FREE:
        free_data['is_current'] = True
    else:
        free_data['is_current'] = False
    plans_data.append(free_data)

    # PRO тариф
    pro_data = {
        'name': pro_plan.name,
        'limits': pro_plan.limits or {},
        'is_pro_plan': True,
        'is_active': is_pro_active,
    }
    plans_data.append(pro_data)

    context = {
        'plans': plans_data,
        'current_plan': current_plan.name,
        'is_pro_active': is_pro_active,
    }

    return render(request, 'plans/pricing.html', context)
