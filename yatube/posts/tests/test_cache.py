from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostsCacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="NoName")
        cls.group = Group.objects.create(
            title="Тестовый заголовок группы",
            slug="test-slug",
            description="Тестовое описание",
        )
        # Создадим запись в БД
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_cache_index(self):
        """Проверяем корректную работу кэша на главной странице"""
        response_first = self.authorized_client.get(reverse("posts:index"))
        post_1 = Post.objects.get(pk=1)
        post_1.text = "Измененный текст"
        post_1.save()
        response_second = self.authorized_client.get(reverse("posts:index"))
        self.assertEqual(response_first.content, response_second.content)
        cache.clear()
        response_third = self.authorized_client.get(reverse("posts:index"))
        self.assertNotEqual(response_first.content, response_third.content)
