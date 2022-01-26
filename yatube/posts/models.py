from django.contrib.auth import get_user_model
from django.db import models
from .validators import validate_not_empty
from django.conf import settings
from core.models import CreatedModel
from django.db.models.constraints import UniqueConstraint

User = get_user_model()
SYMBOLS = settings.SYMBOLS_FOR_TEXT_POST_STR


class Post(models.Model):
    """
    Класс Post используется для создания моделей Post
    (пост в социальной сети).
    """
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста',
        max_length=10000,
        validators=[validate_not_empty],
        blank=False
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        related_name='postsin',
        blank=True,
        null=True,
        verbose_name='Выбрать группу',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """
        Внутренний класс Meta для хранения метаданных
        класса Post.
        """
        ordering = ['-pub_date', '-pk']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        return self.text[:SYMBOLS]


class Group(models.Model):
    """
    Класс Group используется для создания моделей Group
    сообществ, в которых происходит размещение постов
    в социальной сети.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Comment(CreatedModel):
    """
    Класс Comment используется для создания моделей Comment
    комментариев, которые размещаются под постами.
    """
    post = models.ForeignKey(
        Post,
        verbose_name='Комментарии',
        on_delete=models.CASCADE,
        related_name='comments',
        blank=False,
        null=False
    )
    author = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        max_length=20000,
        verbose_name='Tекст комментария',
        help_text='Введите комментарий',
        validators=[validate_not_empty],
        blank=False
    )

    class Meta:
        """
        Внутренний класс Meta для хранения метаданных
        класса Comment.
        """
        ordering = ['-created', '-pk']

    def __str__(self) -> str:
        return self.text[:SYMBOLS]


class Follow(CreatedModel):
    """
    Класс Follow используется для создания моделей Follow
    подписок на авторов.
    """
    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='подписка',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        """
        Внутренний класс Meta для хранения метаданных
        класса Follow.
        """
        UniqueConstraint(fields=['user', 'author'], name='unique_follow')

    def __str__(self) -> str:
        return self.author.username
