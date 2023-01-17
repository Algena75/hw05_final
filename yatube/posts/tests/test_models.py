from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост более 15 символов',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name_post = post.text[:15]
        self.assertEqual(expected_object_name_post, str(post))

    def test_verbose_name(self):
        """verbose_name в полях POST совпадает с ожидаемым."""
        post = PostModelTest.post
        self.assertEqual(
            post._meta.get_field('text').verbose_name, 'Текст поста'
        )

    def test_help_text(self):
        """help_text в полях POST совпадает с ожидаемым."""
        post = PostModelTest.post
        self.assertEqual(
            post._meta.get_field('text').help_text, 'Введите текст поста'
        )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name_group = group.title
        self.assertEqual(expected_object_name_group, str(group))

    def test_verbose_name(self):
        """verbose_name в полях Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        self.assertEqual(
            group._meta.get_field('slug').verbose_name, 'уникальный адрес')

    def test_help_text(self):
        """help_text в полях Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        self.assertEqual(
            group._meta.get_field('slug').help_text, 'адрес')
