from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.user_auth = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост Более 15 символов',
        )

    def setUp(self):
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.user)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_auth)

    def test_pages_exist_at_desired_location(self):
        """Общедоступные страницы доступны по ожидаемому адресу."""
        cache.clear()
        pages_address = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user}/',
            f'/posts/{self.post.id}/',
        ]
        for address in pages_address:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_nonexistent_page_has_status_404(self):
        """Несуществующая страница возвращает статус 404."""
        response = self.guest_client.get('/nonexistent_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_create_post_url_exists_at_desired_location_authorized(self):
        """Страница создания поста доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_edit_post_page_exists_at_desired_location_author(self):
        """Страница редактирования поста доступна автору."""
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_edit_post_page_redirects_if_not_author(self):
        """Страница редактирования пересылает на страницу поста не автора."""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_edit_post_page_redirects_if_guest_client(self):
        """Страница редактирования пересылает на страницу login гостя."""
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next="
            f"{reverse('posts:post_edit',kwargs={'post_id': self.post.id})}"
        )

    def test_create_post_url_exists_at_desired_location_authorized(self):
        """Страница создания поста пересылает на страницу login."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={reverse('posts:post_create')}"
        )

    def test_urls_use_correct_template(self):
        """URL использует правильный шаблон."""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_follow_page_exist_at_desired_location(self):
        """Страница избранных авторов доступна по ожидаемому адресу."""
        response = self.authorized_client.get('/follow/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_comments_page_exist_and_redirects(self):
        """Страница комментирования доступна по ожидаемому адресу."""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/comment/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_follow_pages_exist_and_redirects(self):
        """Страницы подписки доступны по ожидаемому
        адресу и переадресуют на страницу профайла."""
        pages_address = [
            f'/profile/{self.user}/follow/',
            f'/profile/{self.user}/unfollow/',
        ]
        for address in pages_address:
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertRedirects(response, f'/profile/{self.user}/')
