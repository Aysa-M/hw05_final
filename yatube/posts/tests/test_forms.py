import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings

from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
ABSTRACT_OBJECT = settings.ABSTRACT_CREATED_OBJECT_FOR_TESTS


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):
    """
    Класс для создания тестов для проверки корректной работы
    форм приложения posts.
    """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_second = User.objects.create_user(username='Aysa')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_second = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-second',
            description='Тестовое описание 2',
        )
        test_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                    b'\x01\x00\x80\x00\x00\x00\x00\x00'
                    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                    b'\x0A\x00\x3B')
        cls.uploaded = SimpleUploadedFile(
            name='test.gif',
            content=test_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста для forms.',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded,
        )
        cls.form = PostForm()
        cls.profile_username = cls.user.username
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_second,
            text='Комментарий к посту про forms'
        )
        cls.comment_form = CommentForm()

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_second = Client()
        self.authorized_client_second.force_login(self.user_second)

    def test_form_posts_create_post_without_image(self):
        """
        Проверка создания новой записи в базе данных
        при отправке валидной формы со страницы создания данного
        поста без картинки.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Post in da home',
            'group': self.group_second.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.profile_username})
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + ABSTRACT_OBJECT)
        ordered_posts = Post.objects.order_by('id')
        last_post = ordered_posts.last()
        self.assertEqual(form_data['text'], last_post.text)
        self.assertEqual(form_data['group'], last_post.group.pk)

    def test_form_posts_create_post_with_image(self):
        """
        Проверка создания новой записи в базе данных
        при отправке валидной формы со страницы создания данного
        поста с картинкой.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Post in da home',
            'group': self.group_second.pk,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.profile_username})
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + ABSTRACT_OBJECT)
        ordered_posts = Post.objects.order_by('id')
        last_post = ordered_posts.last()
        self.assertTrue(Post.objects.filter(
            text=last_post.text,
            group=last_post.group.pk,
            image=last_post.image).exists())

    def test_form_posts_edit_post(self):
        """
        Проверка изменения существующего поста в базе данных при
        отправке валидной формы со страницы редактирования
        поста.
        """
        post_count = Post.objects.count()
        form_data_edit = {
            'text': 'Edited текст поста для forms.',
            'group': self.group_second.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data_edit,
            is_edit=True,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.pk})
        )
        self.assertEqual(Post.objects.count(), post_count)
        edited_post = Post.objects.get(id=self.post.pk)
        self.assertEqual(form_data_edit['text'],
                         edited_post.text)
        self.assertEqual(form_data_edit['group'],
                         edited_post.group.pk)

    def test_form_posts_edit_post_by_not_author(self):
        """
        Проверка невозможности изменения существующего поста
        в базе данных при отправке валидной формы со страницы редактирования
        поста незарегистрированным пользователем.
        """
        post_count = Post.objects.count()
        form_data_edit = {
            'text': 'Edited текст поста для forms не автором.',
            'group': self.group_second.pk,
        }
        response = self.authorized_client_second.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data_edit,
            is_edit=False,
            follow=False
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND,
                         'Пользователь не является автором поста.'
                         'Редактирование поста запрещено.'
                         'Перенаправление невозможно.')
        self.assertEqual(Post.objects.count(), post_count)
        edited_post = Post.objects.get(id=self.post.pk)
        self.assertNotEqual(form_data_edit['text'],
                            edited_post.text)
        self.assertNotEqual(form_data_edit['group'],
                            edited_post.group.pk)

    def test_form_posts_create_post_by_anonymous(self):
        """
        Проверка создания нового поста незарегистрированным клиентом
        в базе данных при отправке валидной формы со страницы создания данного
        поста. Пост не должен создаться.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Post by anonymous',
            'group': self.group.pk,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=False,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND,
                         'Пользователь не зарегистрирован.'
                         'Создание поста запрещено.'
                         'Перенаправление невозможно.')
        self.assertEqual(
            Post.objects.count(),
            post_count)

    def test_form_posts_edit_post_by_anonymous(self):
        """
        Проверка невозможности изменения существующего поста
        в базе данных при отправке валидной формы со страницы редактирования
        поста незарегистрированным пользователем.
        """
        post_count = Post.objects.count()
        form_data_edit = {
            'text': 'Edited текст поста для forms анонимом.',
            'group': '',
        }
        response = self.client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data_edit,
            is_edit=False,
            follow=False)
        self.assertEqual(response.status_code, HTTPStatus.FOUND,
                         'Пользователь не зарегистрирован.'
                         'Редактирование поста запрещено.'
                         'Перенаправление невозможно.')
        self.assertEqual(Post.objects.count(), post_count)
        edited_post = Post.objects.get(id=self.post.pk)
        self.assertNotEqual(form_data_edit['text'],
                            edited_post.text)
        self.assertNotEqual(form_data_edit['group'],
                            edited_post.group.pk)

    def test_views_posts_add_comment_authorized_only(self):
        """
        Проверка функции комментирования поста только авторизованным
        пользователем.
        """
        comment_count = Comment.objects.count()
        if self.comment.author == self.authorized_client:
            form_data = {
                'text': 'That post is boring.'
            }
            response = self.authorized_client.post(reverse(
                'posts:add_comment'),
                data=form_data,
                follow=True,
            )
            self.assertRedirects(response, reverse('posts:post_detail'))
            self.assertEqual(Comment.objects.count(),
                             comment_count + ABSTRACT_OBJECT)
            ordered_comments = Comment.objects.order_by('id')
            last_comment = ordered_comments.last()
            self.assertTrue(Comment.objects.filter(
                            text=last_comment.text).exists())

    def test_form_posts_comment_by_anonymous(self):
        """
        Проверка функции комментирования поста незарегистрированным клиентом
        в базе данных при отправке валидной формы со страницы.
        Комментарий не должен создаться.
        """
        comment_count = Comment.objects.count()
        if self.comment.author != self.authorized_client:
            form_data = {
                'text': 'This post must not be commented.'
            }
            response = self.client.post(reverse(
                'posts:add_comment', kwargs={'post_id': self.post.pk}),
                data=form_data,
                follow=False,
            )
            self.assertEqual(response.status_code, HTTPStatus.FOUND,
                             'Пользователь не зарегистрирован.'
                             'Создание комментария запрещено.'
                             'Перенаправление невозможно.')
            self.assertEqual(Comment.objects.count(), comment_count)
