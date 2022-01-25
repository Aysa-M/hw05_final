from django import template
from django.shortcuts import redirect

register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={'class': css})


def authorized_only(func):
    def check_user(request, *args, **kwargs):
        if request.user.is_authenticated:
            return func(request, *args, **kwargs)
        else:
            return redirect('/auth/login/')
    return check_user
