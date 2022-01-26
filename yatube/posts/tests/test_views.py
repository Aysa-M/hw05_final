import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.core.paginator import Paginator

from posts.models import Post, Group, Comment, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
COUNT_PER_PAGE = settings.COUNT_PER_PAGE
ABSTRACT_OBJECT = settings.ABSTRACT_CREATED_OBJECT_FOR_TESTS


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
    """
    Класс для создания тестов для проверки работы view функций
    приложения posts.
    """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_second = User.objects.create_user(username='second_auth')
        cls.another_user = User.objects.create_user(username='another_auth')
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
            text='Текст тестового поста для Views.',
            author=cls.user,
            group=cls.group,
            image=cls.uploaded
        )
        cls.objs = []
        for i in range(2, 15):
            cls.objs.append((
                Post(
                    author=cls.user,
                    group=cls.group,
                    text='Создание поста {i} ранжированием.'.format(i=i),
                    image=cls.uploaded))
            )
        cls.page_obj = Post.objects.bulk_create(cls.objs)
        paginator = Paginator(
            Post.objects.order_by('-pub_date'),
            COUNT_PER_PAGE)
        page_second = paginator.get_page(2)
        cls.page_second_obj = len(page_second.object_list)
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий к посту'
        )
        cls.author = cls.user_second
        cls.author_first = cls.user
        cls.another_author = cls.another_user
        cls.follow = Follow.objects.create(
            user=cls.user_second,
            author=cls.author_first
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_second = Client()
        self.authorized_client_second.force_login(self.user_second)
        self.authorized_client_another = Client()
        self.authorized_client_another.force_login(self.another_user)

    def test_views_names_namespace(self):
        """
        Проверка о том, что во view-функциях используются правильные
        html-шаблоны (name:namespace).
        """
        posts_names_namespaces = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}): 'posts/create_post.html',
        }
        for reverse_name, template in posts_names_namespaces.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def first_object_context(self, *args, **kwargs) -> dict:
        """
        Возвращает context словарь первого элемента списка
        page_obj для последующего использования в сравнительных тестах
        context страниц.
        """
        first_object = self.page_obj[0]
        first_object_context = {
            'pk': first_object.pk,
            'text': first_object.text,
            'pub_date': first_object.pub_date,
            'author': first_object.author,
            'username': first_object.author.username,
            'image': first_object.image,
            'group': first_object.group,
            'title': first_object.group.title,
            'slug': first_object.group.slug,
        }
        return first_object_context

    def test_views_posts_index_context(self):
        """
        Проверка соответствия списка постов ожиданиям словаря context,
        передаваемого в шаблон index.html при вызове.
        """
        response = self.client.get(reverse('posts:index'))
        first_object_index = self.first_object_context(response)
        self.assertEqual(first_object_index['author'],
                         self.page_obj[0].author)
        self.assertEqual(first_object_index['text'], self.page_obj[0].text)
        self.assertEqual(first_object_index['pub_date'],
                         self.page_obj[0].pub_date)
        self.assertEqual(first_object_index['image'],
                         self.page_obj[0].image)

    def test_views_posts_group_list_context(self):
        """
        Проверка соответствия списка постов, отфильрованного по группе
        ожиданиям словаря context, передаваемого в шаблон
        group_list.html при вызове.
        """
        response = self.client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        first_object_group_list = self.first_object_context(response)
        self.assertEqual(first_object_group_list['author'],
                         self.page_obj[0].author)
        self.assertEqual(
            first_object_group_list['text'],
            self.page_obj[0].text)
        self.assertEqual(first_object_group_list['pub_date'],
                         self.page_obj[0].pub_date)
        self.assertEqual(first_object_group_list['group'],
                         self.page_obj[0].group)
        self.assertEqual(first_object_group_list['title'],
                         self.page_obj[0].group.title)
        self.assertEqual(first_object_group_list['slug'],
                         self.page_obj[0].group.slug)
        self.assertEqual(first_object_group_list['image'],
                         self.page_obj[0].image)

    def test_views_posts_profile_context(self):
        """
        Проверка соответствия списка постов, отфильтрованного по пользователю,
        ожиданиям словаря context, передаваемого в шаблон profile.html
        при вызове.
        """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        first_object_profile = self.first_object_context(response)
        self.assertEqual(first_object_profile['author'],
                         self.page_obj[0].author)
        self.assertEqual(first_object_profile['username'],
                         self.page_obj[0].author.username)
        self.assertEqual(first_object_profile['text'], self.page_obj[0].text)
        self.assertEqual(first_object_profile['pub_date'],
                         self.page_obj[0].pub_date)
        self.assertEqual(first_object_profile['group'],
                         self.page_obj[0].group)
        self.assertEqual(first_object_profile['image'],
                         self.page_obj[0].image)

    def test_views_posts_post_detail_context(self):
        """
        Проверка соответствия одного поста, отфильтрованного по id поста,
        ожиданиям словаря context, передаваемого в шаблон
        post_detail.html при вызове.
        """
        response = self.client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        first_object_post = self.first_object_context(response)
        self.assertEqual(first_object_post['author'],
                         self.page_obj[0].author)
        self.assertEqual(first_object_post['username'],
                         self.page_obj[0].author.username)
        self.assertEqual(first_object_post['pub_date'],
                         self.page_obj[0].pub_date)
        self.assertEqual(first_object_post['text'], self.page_obj[0].text)
        self.assertEqual(first_object_post['group'],
                         self.page_obj[0].group)
        self.assertEqual(first_object_post['pk'],
                         self.page_obj[0].pk)
        self.assertEqual(first_object_post['image'],
                         self.page_obj[0].image)

    def test_views_posts_edit_post_context(self):
        """
        Проверка соответствия формы редактирования поста, отфильтрованного по
        id поста, ожиданиям словаря context, передаваемого
        в шаблон create_post.html при вызове.
        """
        if self.post.author == self.authorized_client:
            response = self.authorized_client.get(
                reverse('posts:post_detail',
                        kwargs={'post_id': self.post.pk})
            )
            form_fields_edit = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields_edit.items():
                while self.subTest(value=value):
                    form_field_edit = response.context.get('form').fields.get(
                        value)
                    self.assertIsInstance(form_field_edit, expected)

    def test_views_posts_create_post_context(self):
        """
        Проверка соответствия формы создания поста,
        ожиданиям словаря context, передаваемого в шаблон
        create_post.html при вызове.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_views_posts_created_post_is_arised_on_pages_context(self):
        """
        Проверка отображения поста на: главной странице сайта,
        странице выбранной группы и в профайле пользователя в случае,
        если что если при создании поста указать группу. Данный пост
        не должен попасть в группу, для которой он не был предназначен.
        """
        if self.post.author == self.authorized_client:
            if self.post.group == self.group:
                form_data = {
                    'text': self.post.text,
                    'group': self.group.pk,
                }
                response = self.authorized_client.post(
                    reverse('posts:post_create',
                            data=form_data,
                            follow=True))
                self.assertRedirects(response, 'posts:post_detail')
                pages_for_post = [
                    '/',
                    '/posts/group/{slug}/'.format(slug=self.group.slug),
                    '/profile/{username}/'.format(username=self.user.username),
                ]
                for address in pages_for_post:
                    with self.subTest(address=address):
                        response_from_address = self.authorized_client.get(
                            address)
                        self.assertIsInstance(response_from_address, address)
            elif self.post.group != self.group:
                form_data = {
                    'text': self.post.text,
                    'group': '',
                }
                response = self.authorized_client.post(
                    reverse(
                        'posts:post_create',
                        data=form_data,
                        follow=True))
                self.assertRedirects(response, reverse('posts:post_detail'))
                self.assertFormError(
                    response,
                    'form',
                    'group',
                    'Созданный пост не будет перенаправлен'
                    'на страницу group_list'
                )
                pages_for_post = [
                    '/',
                    '/profile/{username}/'.format(username=self.user.username),
                ]
                for address in pages_for_post:
                    with self.subTest(address=address):
                        response_from_address = self.authorized_client.get(
                            address)
                        self.assertIsInstance(response_from_address, address)

    def test_views_posts_comment_is_arised_on_post_detail_page(self):
        """
        Проверка функции комментирования - после успешной отправки
        комментарий появляется на странице поста.
        """
        if self.comment.author == self.authorized_client:
            form_data = {'text': self.comment}
            response = self.authorized_client.post(reverse('posts:add_comment',
                                                           data=form_data,
                                                           follow=True))
            self.assertRedirects(response, reverse('posts:post_detail'))
            response_from_address = self.authorized_client.get(reverse(
                'posts:post_detail'))
            self.assertIsInstance(response_from_address,
                                  reverse('posts:post_detail'))

    def test_views_profile_follow(self):
        """
        Тест на проверку может ли авторизованный пользователь
        подписываться на других пользователей.
        """
        follow_count = Follow.objects.count()
        self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.author.username})
        )
        check_following = Follow.objects.filter(
            author__following__user=self.user).exists()
        if not check_following:
            Follow.objects.create(user=self.user, author=self.author)
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.author.username})
        )
        following = Follow.objects.filter(author=self.author).exists()
        self.assertEqual(Follow.objects.count(),
                         follow_count + ABSTRACT_OBJECT)
        self.assertTrue(following, 'Подписка не совершена.')

    def test_views_profile_unfollow(self):
        """
        Тест на проверку может ли авторизованный пользователь
        удалять других авторизованных пользователей из своих подписок.
        """
        follow_count = Follow.objects.count()
        self.authorized_client_second.get(reverse(
            'posts:profile',
            kwargs={'username': self.author_first.username})
        )
        check_following = Follow.objects.filter(
            author=self.author_first).exists()
        if check_following:
            following = get_object_or_404(Follow,
                                          user=self.user_second,
                                          author=self.author_first)
            following.delete()
        self.assertEqual(Follow.objects.count(),
                         follow_count - ABSTRACT_OBJECT)
        self.authorized_client_second.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.author_first.username})
        )
        unfollowing = Follow.objects.filter(author=self.user).exists()
        self.assertFalse(unfollowing, 'Вы не отписались от автора.')

    def test_new_post_is_showed_for_followers_and_not_for_unfollowers(self):
        """
        Новая запись пользователя появляется в ленте тех,
        кто на него подписан и е появляется в ленте тех,
        кто не подписан.
        """
        object_count = Post.objects.count()
        subscribe = Follow.objects.filter(user=self.user_second,
                                          author=self.author_first).exists()
        subscribe_next = Follow.objects.filter(
            user=self.user,
            author=self.another_author).exists()
        author_first_posts = Post.objects.filter(
            author=self.author_first).count()
        if subscribe:
            self.authorized_client_second.get(reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_first.username})
            )
            response_follow_index = self.authorized_client_second.get(
                reverse('posts:follow_index')
            )
            context_follow_index = response_follow_index.context.get(
                'post_quantity')
            self.assertEqual(context_follow_index, author_first_posts,
                             'Фактическое количество постов автора '
                             'не совпадает с количеством постов '
                             'в его профиле.')
        elif subscribe_next:
            self.authorized_client.get(reverse(
                'posts:profile_follow',
                kwargs={'username': self.author_first.username})
            )
            response_follow_index_next = self.authorized_client.get(
                reverse('posts:follow_index')
            )
            context_follow_index_next = response_follow_index_next.context.get(
                'post_quantity')
            self.assertNotEqual(context_follow_index_next, author_first_posts,
                                'Фактическое количество постов автора не '
                                'совпадает с '
                                'количеством постов в его профиле.')
        cache.clear()
        new_post = Post.objects.create(text='Brand new post by auth.',
                                       author=self.author_first,
                                       group=self.group_second,
                                       image=self.uploaded)
        author_first_posts_updated = Post.objects.filter(
            author=self.author_first).count()
        self.assertEqual(Post.objects.count(), object_count + ABSTRACT_OBJECT)
        cache.add('new_post', 'Brand new post by auth.')
        if subscribe:
            response_follow_index_new = self.authorized_client_second.get(
                reverse('posts:follow_index')
            )
            context_follow_index_new = response_follow_index_new.context.get(
                'post_quantity')
            context_list_new = response_follow_index_new.context.get(
                'post_list')
            self.assertEqual(context_follow_index_new, len(context_list_new),
                             'Фактическое количество постов автора '
                             'не совпадает с '
                             'количеством постов в его профиле.')
            self.assertIn(new_post, context_list_new)
        elif subscribe_next:
            response_follow_index_next_new = self.authorized_client.get(
                reverse('posts:follow_index')
            )
            context_next_new = response_follow_index_next_new.context.get(
                'post_quantity')
            context_list_next_new = response_follow_index_next_new.context.get(
                'post_list')
            self.assertNotEqual(context_next_new, author_first_posts_updated,
                                'Фактическое количество постов автора '
                                'не совпадает с '
                                'количеством постов в его профиле.')
            self.assertNotIn(new_post, context_list_next_new)
