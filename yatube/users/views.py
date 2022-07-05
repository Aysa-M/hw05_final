from django.contrib.auth.views import (PasswordResetView,
                                       PasswordChangeView,
                                       PasswordResetConfirmView)
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import (CreationForm,
                    ChangePasswordForm,
                    ResetPasswordForm,
                    PasswordResetConfirmForm)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PasswordChange(PasswordChangeView):
    form_class = ChangePasswordForm
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password_change_form.html'


class PasswordReset(PasswordResetView):
    form_class = ResetPasswordForm
    success_url = reverse_lazy('users:password_reset_done')
    template_name = 'users/password_reset_form.html'


class PasswordResetConfirm(PasswordResetConfirmView):
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('users:password_reset_complete')
    template_name = 'users/password_reset_complete.html'
