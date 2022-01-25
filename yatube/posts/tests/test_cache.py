from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()
COUNT_PER_PAGE = settings.COUNT_PER_PAGE
ABSTRACT_OBJECT = settings.ABSTRACT_CREATED_OBJECT_FOR_TESTS


class CacheTest(TestCase):
    """Класс для создания тестов для проверки работы cache."""
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
            text='Текст тестового поста для Cache.',
            author=cls.user,
            group=cls.group,
        )
        cls.objs = []
        for i in range(1, 14):
            cls.objs.append((
                Post(
                    author=cls.user,
                    group=cls.group,
                    text='{i} Создание поста для кэша.'.format(i=i)
                )))
        cls.post_obj = Post.objects.bulk_create(cls.objs)
        paginator = Paginator(
            Post.objects.order_by('-pub_date'),
            COUNT_PER_PAGE)
        page = paginator.get_page(1)
        cls.page_first = len(page.object_list)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """Тест для проверки кеширования главной страницы index."""
        object_count = Post.objects.count()
        response_predelete = self.client.get(reverse('posts:index'))
        cached_object = Post.objects.order_by('id')
        cached_object = cached_object.last()
        cached_object_dict = {
            'text': cached_object.text,
        }
        self.assertEqual(cached_object_dict['text'], self.post_obj[-1].text)
        self.assertIn(cached_object.text, response_predelete.content.decode())
        Post.objects.filter(pk=cached_object.pk).delete()
        response_deleted = self.client.get(reverse('posts:index'))
        content_deleted = response_deleted.content
        self.assertEqual(Post.objects.count(), object_count - ABSTRACT_OBJECT)
        self.assertEqual(response_predelete.content, content_deleted)
        cache.clear()
        response_cached = self.client.get(reverse('posts:index'))
        content_cached = response_cached.content
        self.assertNotEqual(content_deleted, content_cached)
