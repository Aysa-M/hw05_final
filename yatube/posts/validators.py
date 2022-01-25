from django import forms


def validate_not_empty(value):
    if value == '':
        raise forms.ValidationError(
            'Заполните поле "Текст".',
            params={'value': value},
        )
