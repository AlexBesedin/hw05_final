from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Follow, Group, Post, User


class PostsPagesTests(TestCase):
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

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.close()
        group = PostsPagesTests.group
        user = PostsPagesTests.user
        post = PostsPagesTests.post
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    args=[group.slug]): 'posts/group_list.html',
            reverse(
                'posts:profile', args=[user.username]
            ): 'posts/profile.html',
            reverse('posts:post_detail',
                    args=[post.pk]): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    args=[post.pk]): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_group_0 = first_object.group.title
        self.assertEqual(post_text_0, "Тестовый пост")
        self.assertEqual(post_author_0, "NoName")
        self.assertEqual(post_group_0, "Тестовый заголовок группы")

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                "posts:group_list", args=[self.group.slug])
        )
        expected = list(Post.objects.filter(group_id=self.group.id)[:10])
        self.assertEqual(list(response.context["page_obj"]), expected)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:profile", kwargs={"username": self.post.author})
        )
        first_object = response.context["page_obj"][0]
        post_text_0 = first_object.text
        self.assertEqual(response.context["author"].username, "NoName")
        self.assertEqual(post_text_0, "Тестовый пост")

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.context.get("post").text, self.post.text)
        self.assertEqual(response.context.get("post").author, self.post.author)
        self.assertEqual(response.context.get("post").group, self.post.group)

    def test_create_post_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_check_group_in_pages(self):
        """Проверяем появление поста на / главной странице сайта /
        странице выбранной группы,/ в профайле пользователя
        / с выбранной группой"""
        form_fields = {
            reverse("posts:index"): Post.objects.get(group=self.post.group),
            reverse(
                "posts:group_list", args=[self.group.slug]
            ): Post.objects.get(group=self.post.group),
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context["page_obj"]
                self.assertIn(expected, form_field)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PAGE_NUBMER = 13
        cls.user = User.objects.create_user(username="AnonNoName")
        cls.group = Group.objects.create(
            title="Тестовый заголовок группы2",
            slug="test-slug2",
            description="Тестовое описание группы2",
        )
        cls.post = Post.objects.bulk_create(
            [
                Post(
                    text=f"Тестовый текст{i}",
                    author=cls.user,
                    group=cls.group
                )
                for i in range(cls.PAGE_NUBMER)
            ]
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()

    def test_first_page_contains_ten_records(self):
        NUMBER_POSTS = 10
        templates_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group_list.html": reverse(
                "posts:group_list", args=[self.group.slug]
            ),
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": "AnonNoName"}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context["page_obj"]),
                    NUMBER_POSTS
                )

    def test_second_page_contains_three_records(self):
        NUMBER_POSTS = 3
        templates_pages_names = {
            "posts/index.html": reverse("posts:index") + "?page=2",
            "posts/group_list.html": reverse(
                "posts:group_list", args=[self.group.slug]
            )
            + "?page=2",
            "posts/profile.html": reverse(
                "posts:profile", kwargs={"username": "AnonNoName"}
            )
            + "?page=2",
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context["page_obj"]),
                    NUMBER_POSTS
                ),

    class FollowTests(TestCase):
        def setUp(self):
            self.authorized_client_follower = Client()
            self.authorized_client_following = Client()
            self.user_follower = User.objects.create(username="follower")
            self.user_following = User.objects.create(username="following")
            self.post = Post.objects.create(
                author=self.user_following,
                text="Тестовая запись  для подписчиков"
            )
            self.authorized_client_follower.force_login(
                self.user_follower
            )
            self.authorized_client_following.force_login(
                self.user_following
            )

        def test_post_profile_follow(self):
            self.authorized_client_follower.get(
                reverse(
                    "posts:profile_follow",
                    kwargs={"username": self.user_following.username},
                )
            )
            self.assertEqual(Follow.objects.all().count(), 1)

        def test_post_profile_unfollow(self):
            self.authorized_client_follower.get(
                reverse(
                    "posts:profile_follow",
                    kwargs={"username": self.user_following.username},
                )
            )
            self.authorized_client_follower.get(
                reverse(
                    "posts:profile_unfollow",
                    kwargs={"username": self.user_following.username},
                )
            )
            self.assertEqual(Follow.objects.all().count(), 0)

        def test_post_follow_index_follower(self):
            """Запись появляется в ленте подписчиков."""
            Follow.objects.create(
                user=self.user_follower,
                author=self.user_following
            )
            response = self.authorized_client_follower.get("/follow/")
            post_text_0 = response.context["page_obj"][0].text
            self.assertEqual(post_text_0,
                             "Тестовая запись для тестирования ленты")
            # проверка, что запись не появилась у неподписанного пользователя
            response = self.authorized_client_following.get("/follow/")
            self.assertNotEqual(response,
                                "Тестовая запись для тестирования ленты")

        def test_post_comment_authorized_user(self):
            """Проверка добавления комментария."""
            self.authorized_client_following.post(
                f"/posts/{self.post.pk}/comment/",
                {"text": "тестовый комментарий"},
                follow=True,
            )
            response = self.authorized_client_following.get(
                f"/posts/{self.post.pk}/"
            )
            self.assertContains(response, "тестовый комментарий")
            self.authorized_client_following.logout()
            self.authorized_client_following.post(
                f"/posts/{self.post.pk}/comment/",
                {"text": "комментарий от юзера"},
                follow=True,
            )
            response = self.authorized_client_following.get(
                f"/posts/{self.post.pk}/"
            )
            self.assertNotContains(response, "комментарий от юзера")