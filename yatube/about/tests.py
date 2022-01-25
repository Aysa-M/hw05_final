from django.test import TestCase
from http import HTTPStatus
from django.urls import reverse


class StaticURLTests(TestCase):
    """Класс для создания тестов URL-адресов приложения about."""
    def test_urls_about(self):
        """Проверка доступности URL-адресов приложения about."""
        url_about = [
            '/about/author/',
            '/about/tech/',
        ]
        for address in url_about:
            with self.subTest(address=address):
                response = self.client.get(address)
                if response.status_code == HTTPStatus.OK:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND)

    def test_templates_about(self):
        """URL-адрес использует соответствующие шаблоны about."""
        templates_about = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_about.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)


class AboutViewsTests(TestCase):
    """Класс для создания тестов View-функций приложения about."""
    def test_views_about_names_namespace(self):
        """
        Проверка правильности используемых name:namespaces
        в html-шаблонах about.
        """
        about_names_namespaces = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in about_names_namespaces.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
