from http import HTTPStatus
from django.test import TestCase


class ViewsTestClass(TestCase):
    """
    Класс используется для создания тестов по проверке
    работы views функций приложения core.
    """
    def test_page_not_found_404_is_accessed(self):
        """
        Проверяет доступность страницы ошибки 404 при ее возникновении.
        """
        response = self.client.get('/unexpected_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_page_not_found_404_used_proper_template(self):
        """
        Проверяет использование правильного шаблона для отображения
        страницы ошибки 404.
        """
        response = self.client.get('/unexpected_page/')
        self.assertTemplateUsed(response, 'core/404.html')
