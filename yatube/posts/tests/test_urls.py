from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="NoName")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        # Создадим запись в БД тестовый пост
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            id=3,
        )

        cls.templates = [
            "/",
            f"/group/{URLTests.group.slug}/",
            f"/profile/{URLTests.user}/",
            f"/posts/{URLTests.post.id}/",
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_url_names = {
            "posts/index.html": "/",
            "posts/group_list.html": f"/group/{URLTests.group.slug}/",
            "posts/profile.html": f"/profile/{URLTests.user.username}/",
            "posts/post_detail.html": f"/posts/{URLTests.post.id}/",
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_posts_post_id_edit_url_exists_at_author(self):
        """Страница /posts/post_id/edit/ доступна только автору."""
        response = self.authorized_client.get(f"/posts/{self.post.id}/edit/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_guest(self):
        """Страница posts/post_id/edit/ перенаправляет
        неавторизованного клиента на страницу авторизации."""
        response = self.guest_client.get(
            f"/posts/{self.post.id}/edit/"
        )
        self.assertRedirects(
            response, f"/auth/login/?next=/posts/{self.post.id}/edit/"
        )

    def test_create_url_redirect_guest(self):
        """Страница /create/ перенаправляет неавторизованного клиента
        на страницу авторизации."""
        response = self.guest_client.get("/create/")
        self.assertRedirects(response, "/auth/login/?next=/create/")

    def test_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна только
        авторизованному пользователю."""
        response = self.authorized_client.get(
            reverse("posts:post_create"), follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location(self):
        """Проверяем общедоступные страницы"""
        for url in self.templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_at_desired_location(self):
        """Страница /unexisting_page/ должна выдать ошибку."""
        response = self.guest_client.get("/unexisting_page/")
        self.assertEqual(
            response.status_code, HTTPStatus.NOT_FOUND)
