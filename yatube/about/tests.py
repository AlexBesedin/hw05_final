from http import HTTPStatus

from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованый клиент
        self.guest_client = Client()

    def test_about_and_tech_url_exists_at_desired_location(self):
        """Страница доступа по URL."""
        pages: tuple = ("/about/author/", "/about/tech/")
        for page in pages:
            response = self.guest_client.get(page)
            error_name: str = f"Ошибка: нет доступа до страницы {page}"
            self.assertEqual(response.status_code, HTTPStatus.OK, error_name)

    def test_about_and_tech_url_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names: dict = {
            "/about/author/": "about/author.html",
            "/about/tech/": "about/tech.html",
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                error_name: str = f"Ошибка: {adress} ожидал шаблон {template}"
                self.assertTemplateUsed(response, template, error_name)
