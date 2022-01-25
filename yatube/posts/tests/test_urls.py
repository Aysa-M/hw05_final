from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
    """
    Класс для создания тестов для URL адресов
    приложения posts.
    """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста для URLs.',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_posts_url_exists_at_desired_location_for_guest_client(self):
        """
        Проверка доступности адресов приложения posts для
        неавторизованных пользователей.
        """
        url_names_guest = [
            '/',
            '/posts/group/{slug}/'.format(slug=self.group.slug),
            '/posts/{post_id}/'.format(post_id=self.post.pk),
            '/unexisting_page/',
        ]
        for address in url_names_guest:
            with self.subTest(address=address):
                response = self.client.get(address)
                if response.status_code == HTTPStatus.OK:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND)

    def test_posts_url_exists_at_desired_location_for_authorized_client(self):
        """
        Проверка доступности адресов приложения posts для
        авторизованных пользователей.
        """
        url_names_authorized = [
            '/',
            '/posts/group/{slug}/'.format(slug=self.group.slug),
            '/profile/{username}/'.format(username=self.user.username),
            '/posts/{post_id}/'.format(post_id=self.post.pk),
            '/posts/{post_id}/edit/'.format(post_id=self.post.pk),
            '/create/',
            '/follow/',
            '/unexisting_page/',
        ]
        for address in url_names_authorized:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if response.status_code == HTTPStatus.OK:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND)

    def test_edit_post_by_post_author(self):
        """
        Проверка доступности адреса редактирования поста для
        автора поста.
        """
        response = self.authorized_client.get(
            '/create/',
            args=[self.post.author]
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующие шаблоны posts."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/{slug}/'.format(
                slug=self.group.slug): 'posts/group_list.html',
            '/profile/{username}/'.format(
                username=self.user.username): 'posts/profile.html',
            '/posts/{post_id}/'.format(
                post_id=self.post.pk): 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/{post_id}/edit/'.format(
                post_id=self.post.pk): 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
