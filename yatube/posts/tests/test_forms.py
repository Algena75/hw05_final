import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import CommentForm
from posts.models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_at_post_edit_page_updates_data(self):
        """Проверка изменения данных в записях при отправке формы
        на странице редактирования поста."""
        post = Post.objects.create(
            author=self.user,
            text=('Any text'),
            group=Group.objects.get()
        )
        form_data = {
            'text': 'Post has been changed',
            'group': self.group.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            form_data
        )
        post.refresh_from_db()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])

    def test_new_post_creates_if_form_is_valid(self):
        """Проверка добавления нового поста в базу данных при отправке
        валидной формы."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'New test post',
            'group': self.group.id
        }
        post = self.authorized_client.post(
            reverse('posts:post_create'),
            form_data
        )
        last_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])
        self.assertEqual(last_post.author, self.user)
        self.assertRedirects(
            post, reverse(
                'posts:profile', kwargs={'username': self.user.username}
            )
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsImageTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=('Any text'),
            group=Group.objects.get(),
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_page_context_contains_image(self):
        """В контексте главной страницы передается изображение."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertIn('small', f'{first_object.image}')
        self.assertTrue(
            Post.objects.filter(
                author=self.user,
                text='Any text',
                image='posts/small.gif'
            ).exists()
        )

    def test_group_page_context_contains_image(self):
        """В контексте страницы группы передается изображение."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        first_object = response.context['page_obj'][0]
        self.assertTrue(
            first_object.image == 'posts/small.gif',
            'Изображение в записи отсутствует!'
        )

    def test_profile_page_context_contains_image(self):
        """В контексте страницы profile передается изображение."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        first_object = response.context['page_obj'][0]
        self.assertIsNotNone(first_object.image, 'Изображение отсутствует!')

    def test_post_detail_page_context_contains_image(self):
        """В контексте отдельного поста передается изображение."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context.get('post').image.name, 'posts/small.gif'
        )

    def test_new_post_creates_if_form_with_image_is_valid(self):
        """Проверка добавления нового поста в базу данных при отправке
        валидной формы."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'New test post',
            'image': uploaded,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            form_data
        )
        last_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_post.text, form_data['text'])
        self.assertIsNotNone(last_post.image, 'Изображение отсутствует!')


class CommentFormsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=('Any text'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_can_be_written_by_authorized_client(self):
        form_data = {
            'text': 'Test comment',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            form_data
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        form = response.context['form']
        self.assertTrue(response.context['comments'].exists())
        self.assertIsInstance(form, CommentForm)
        self.assertContains(response, 'Добавить комментарий:')
        self.assertContains(response, 'Test comment')

    def test_comment_can_not_be_written_by_guest_client(self):
        form_data = {
            'text': 'Test comment',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            form_data
        )
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertFalse(response.context['comments'].exists())
        self.assertNotContains(response, 'Добавить комментарий:')
        self.assertNotContains(response, 'Test comment')
