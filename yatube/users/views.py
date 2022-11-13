from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    # После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"


class CustomLoginView(LoginView):
    """Страница входа в аккаунт."""

    template_name = "users/login.html"


class CustomLogoutView(LogoutView):
    """Страница выхода из аккаунта."""

    template_name = "users/logged_out.html"


class CustomPasswordResetView(PasswordResetView):
    """При сбросе пароля."""

    success_url = reverse_lazy("users:password_reset_done")
    template_name = "users/password_reset_form.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Страница сброса пароля."""

    success_url = reverse_lazy("users:password_reset_complete")
    template_name = "users/password_reset_confirm.html"


class CustomPasswordChangeView(PasswordChangeView):
    """Страница подтверждения сброса пароля."""

    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"
