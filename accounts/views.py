"""
Views для регистрации, входа и выхода.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import RegistrationForm, LoginForm


@require_http_methods(['GET', 'POST'])
@ensure_csrf_cookie
def register_view(request):
    """Регистрация. После успешной регистрации — авто-логин и редирект на главную."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            # PRO будет назначен автоматически сигналом (accounts.signals)
            login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(['GET', 'POST'])
@ensure_csrf_cookie
def login_view(request):
    """Вход по username или email."""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            login(request, form.cleaned_data['user'])
            return redirect('index')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@require_GET
def logout_view(request):
    """Выход. Редирект на страницу входа."""
    logout(request)
    return redirect('login')
