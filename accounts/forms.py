"""
Формы регистрации и входа.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegistrationForm(forms.Form):
    """Регистрация: username, email, password, password confirmation."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'autocomplete': 'username',
        }),
        label='Имя пользователя',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'autocomplete': 'email',
        }),
        label='Email',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
            'autocomplete': 'new-password',
        }),
        label='Пароль',
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Подтверждение пароля',
            'autocomplete': 'new-password',
        }),
        label='Подтверждение пароля',
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError('Введите имя пользователя')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Это имя пользователя уже занято')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Введите email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Этот email уже зарегистрирован')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Пароль должен быть не менее 8 символов')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError({'password_confirm': 'Пароли не совпадают'})
        return cleaned_data


class LoginForm(forms.Form):
    """Вход: username или email, password."""
    username_or_email = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Username или Email',
            'autocomplete': 'username',
        }),
        label='Username или Email',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
            'autocomplete': 'current-password',
        }),
        label='Пароль',
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username_or_email')
        password = cleaned_data.get('password')

        if not username_or_email or not password:
            return cleaned_data

        user = None
        if '@' in username_or_email:
            try:
                user = User.objects.get(email__iexact=username_or_email)
            except User.DoesNotExist:
                pass
        else:
            user = User.objects.filter(username__iexact=username_or_email).first()

        if user:
            user = authenticate(username=user.username, password=password)

        if not user:
            raise forms.ValidationError('Неверный username/email или пароль')

        cleaned_data['user'] = user
        return cleaned_data
