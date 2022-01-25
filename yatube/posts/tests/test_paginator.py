from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator

from posts.models import Post, Group

User = get_user_model()
COUNT_PER_PAGE = settings.COUNT_PER_PAGE


class PaginatorViewsTest(TestCase):
    """Класс для создания тестов для проверки работы пагинатора."""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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
        cls.objs = []
        for i in range(1, 14):
            cls.objs.append((
                Post(
                    author=cls.user,
                    group=cls.group,
                    text='Создание поста {i} для paginator.'.format(i=i)
                )))
        cls.post_obj = Post.objects.bulk_create(cls.objs)
        cls.paginator = Paginator(
            Post.objects.order_by('-pub_date'),
            COUNT_PER_PAGE)
        page_second = cls.paginator.get_page(2)
        cls.page_second_obj = len(page_second.object_list)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_index_contains_ten_records(self):
        """
        Проверка паджинатора - вывод определнного количества
        постов на первую страницу index.html.
        """
        if self.authorized_client:
            response = self.authorized_client.get(reverse(
                'posts:index'))
            self.assertEqual(
                len(response.context['page_obj']), COUNT_PER_PAGE)
        else:
            response = self.client.get(
                reverse('posts:index'))
            self.assertEqual(
                len(response.context['page_obj']), COUNT_PER_PAGE)

    def test_second_page_index_contains_three_records(self):
        """
        Проверка паджинатора - вывод последних постов на
        вторую страницу index.html.
        """
        if self.authorized_client:
            response = self.authorized_client.get(
                reverse('posts:index') + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), self.page_second_obj)
        else:
            response = self.client.get(
                reverse('posts:index') + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), self.page_second_obj)

    def test_first_page_group_list_contains_ten_records(self):
        """
        Проверка паджинатора - вывод определнного количества
        постов на первую страницу group_list.html.
        """
        if self.authorized_client:
            response = self.authorized_client.get(reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}))
            self.assertEqual(
                len(response.context['page_obj']), COUNT_PER_PAGE)
        else:
            response = self.client.get(reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}))
            self.assertEqual(
                len(response.context['page_obj']), COUNT_PER_PAGE)

    def test_second_page_group_list_contains_three_records(self):
        """
        Проверка паджинатора - вывод последних постов на
        вторую страницу group_list.html.
        """
        if self.authorized_client:
            response = self.authorized_client.get((reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})) + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), self.page_second_obj)
        else:
            response = self.client.get((reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})) + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), self.page_second_obj)

    def test_first_page_profile_contains_ten_records(self):
        """
        Проверка паджинатора - вывод определнного количества
        постов на первую страницу profile.html.
        """
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(
            len(response.context['page_obj']), COUNT_PER_PAGE)

    def test_second_page_profile_contains_three_records(self):
        """
        Проверка паджинатора - вывод последних постов на
        вторую страницу group_list.html.
        """
        response = self.authorized_client.get((reverse(
            'posts:profile',
            kwargs={'username': self.user.username})) + '?page=2')
        self.assertEqual(
            len(response.context['page_obj']), self.page_second_obj)
