from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from posts.models import Group, Post, Comment

User = get_user_model()
SYMBOLS = settings.SYMBOLS_FOR_TEXT_POST_STR


class PostModelTest(TestCase):
    """Класс для создания тестов моделей приложения posts."""
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
            text='Текст тестового поста для models.',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комментарий к посту про models'
        )

    def test_post_models_method_str(self):
        """
        Проверяем, что у моделей Post корректно работает
        метод __str__. __str__  post - это строчка с содержимым
        post.text[:15].
        """
        test_model_post = PostModelTest.post
        expected_value = test_model_post.text[:SYMBOLS]
        self.assertEqual(expected_value, str(test_model_post))

    def test_group_models_str(self):
        """
        Проверяем, что у модели Group корректно работает метод __str__.
        __str__  group - это строчка с содержимым group.title.
        """
        test_model_group = PostModelTest.group
        expected_value = test_model_group.title
        self.assertEqual(expected_value, str(test_model_group))

    def test_comment_models_str(self):
        """
        Проверяем, что у модели Comment корректно работает метод __str__.
        __str__  comment - это строчка с содержимым:
        text[:SYMBOLS].
        """
        test_model_comment = PostModelTest.comment
        expected_value_text = test_model_comment.text[:SYMBOLS]
        self.assertEqual(expected_value_text, str(test_model_comment))

    def test_models_have_correct_help_text(self):
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        help_text_for_text = self.post._meta.get_field('text').help_text
        help_text_for_group = self.post._meta.get_field('group').help_text
        field_help_text_post = {
            'text': help_text_for_text,
            'group': help_text_for_group,
        }
        for field, expected_value in field_help_text_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value
                )
