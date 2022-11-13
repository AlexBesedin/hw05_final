from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.author = CacheTests.user
        self.author_client = Client()
        self.author_client.force_login(self.author)
        cache.clear()

    def test_cache_index_page(self):
        """Содержимое главной страницы сайта кешируется."""
        new_post = Post.objects.create(
            text='Проверка кеша',
            group=CacheTests.group,
            author=CacheTests.user
        )
        response = self.author_client.get(reverse('posts:index'))
        self.assertContains(response, new_post)
        new_post.delete()
        response = self.author_client.get(reverse('posts:index'))
        self.assertContains(response, new_post)
        cache.clear()
        response = self.author_client.get(reverse('posts:index'))
        self.assertNotContains(response, new_post)
