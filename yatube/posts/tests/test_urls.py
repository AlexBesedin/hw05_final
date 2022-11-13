from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Follow, Group, Post

User = get_user_model()


class PostURLTests(TestCase):
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
            text='Тестовый текст более 15 символов',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = self.user
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_unathorised_pages(self):
        """Тестирует страницы, для которых не нужна авторизация"""
        status_codes = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:profile', kwargs={
                    'username': PostURLTests.user.username
                }
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail', kwargs={
                    'post_id': PostURLTests.post.id
                }
            ): HTTPStatus.OK,
            reverse(
                'posts:group_list', kwargs={
                    'slug': PostURLTests.group.slug
                }
            ): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }
        for address, code in status_codes.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_post_create_page(self):
        """Страница создания поста доступна
        только авторизованным пользователям"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_page(self):
        """Страница реактирования поста доступна только автору"""
        post_id = self.post.id
        response = self.author_client.get(f'/posts/{post_id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_index(self):
        """Страница избранных авторов доступна
        только авторизованным пользователям"""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_follow(self):
        """Функция подписки доступна
        только авторизованным пользователям"""
        username = PostURLTests.user.username
        response = self.authorized_client.get(f'/profile/{username}/follow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_profile_unfollow(self):
        """Функция отписки доступна
        только авторизованным пользователям"""
        Follow.objects.create(
            author=PostURLTests.user,
            user=self.user
        )
        username = self.user.username
        response = self.authorized_client.get(f'/profile/{username}/unfollow/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post_id = self.post.id
        username = self.user.username
        group_slug = self.group.slug
        templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{username}/': 'posts/profile.html',
            f'/posts/{post_id}/': 'posts/post_detail.html',
            f'/group/{group_slug}/': 'posts/group_list.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                error_name = f'Ошибка: нет доступа до страницы {address}'
                self.assertEqual(
                    self.guest_client.get(address).status_code,
                    HTTPStatus.OK,
                    error_name
                )
                self.assertTemplateUsed(
                    self.guest_client.get(address),
                    template,
                    error_name
                )
