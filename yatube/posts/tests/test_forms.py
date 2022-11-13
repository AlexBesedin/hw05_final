import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="NoNoName")
        cls.form = PostCreateFormTests()
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка, что валидная форма создаёт пост"""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Текст записанный в форму",
            "group": self.group.id
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                text="Текст записанный в форму",
                group=self.group.id,
                author=self.user
            ).exists()
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit(self):
        """Проверка, что валидная форма редактирует пост"""
        self.post = Post.objects.create(
            text="Тестовый текст",
            author=self.user,
            group=self.group
        )
        old_text = self.post
        self.group2 = Group.objects.create(
            title="Тестовая группа2",
            slug="test-group",
            description="Описание"
        )
        form_data = {
            "text": "Текст записанный в форму",
            "group": self.group2.id
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", args=(self.post.id,)),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(
            Post.objects.filter(
                group=self.group2.id,
                author=self.user,
                pub_date=self.post.pub_date
            ).exists()
        )
        error_name1 = "Юзер не может изменить содержание поста"
        self.assertNotEqual(old_text.text, form_data["text"], error_name1)
        error_name2 = "Юзер не может изменить группу поста"
        self.assertNotEqual(old_text.group, form_data["group"], error_name2)

    def test_create_post_with_picture(self):
        """Валидная форма создает запись с картинкой"""
        # Подсчитаем количество записей
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )
        form_data = {
            "text": "Тестовый текст",
            "group": self.group.pk,
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse(
                "posts:profile",
                kwargs={"username": PostCreateFormTests.user}
            ),
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        self.assertTrue(
            Post.objects.filter(
                group=PostCreateFormTests.group,
                author=PostCreateFormTests.user,
                text="Тестовый текст",
            ).exists()
        )
