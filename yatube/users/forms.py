from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (PasswordResetForm,
                                       UserCreationForm,
                                       PasswordChangeForm,
                                       SetPasswordForm)

User = get_user_model()


class CreationForm(UserCreationForm):
    """
    Класс для создания формы, предназначенной для регистрации
    нового пользователя на сайте.
    """
    class Meta(UserCreationForm.Meta):
        """
        Переопределенный класс Meta, необходимый для вывода
        полей, обязательных для заполнения в форме регистрации.
        """
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class PasswordChangeForm(PasswordChangeForm):
    """
    Класс для создания формы для смену пароля.
    """
    model = User
    fields = ('old_password', 'new_password1', 'new_password2')


class PasswordResetForm(PasswordResetForm):
    """
    Класс для формы отправки письма со ссылкой на смену пароля.
    """
    model = User
    fields = ('email')


class PasswordResetConfirmForm(SetPasswordForm):
    """
    Класс для формы установки нового пароля по почте.
    """
    model = User
    fields = ('new_password1', 'new_password2')
