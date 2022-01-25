from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """
    Класс для создания формы, предназначенной для создания нового поста.
    """
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """
    Класс для создания формы, предназначенной для создания
    комментариев под постами.
    """
    class Meta:
        model = Comment
        fields = ('text',)
