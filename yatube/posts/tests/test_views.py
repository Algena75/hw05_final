from random import randrange

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Follow, Group, Post

User = get_user_model()


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа №2',
            slug='test-group-slug',
            description='Тестовое описание №2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=Group.objects.get(pk=2)
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def two_objects_comparison(self, first_object):
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, self.user)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.group.title)
        return

    def test_pages_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        template_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
        }
        for reverse_name, template in template_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.two_objects_comparison(first_object)
        self.assertContains(response, 'Последние обновления на сайте')

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        group_description_0 = first_object.group.description
        group_slug_0 = first_object.group.slug
        group_title_0 = first_object.group.title
        self.assertEqual(group_description_0, self.group.description)
        self.assertEqual(group_slug_0, self.group.slug)
        self.assertEqual(group_title_0, self.group.title)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        first_object = response.context['page_obj'][0]
        self.two_objects_comparison(first_object)
        self.assertContains(response, 'Все посты пользователя')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон отдельного поста по id содержит ожидаемые значения."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(
            response.context.get('post').group.title, self.group.title)
        self.assertContains(response, f'Пост {self.post.text[:30]}')

    def test_post_create_page_show_correct_context(self):
        """Шаблон формы создания поста сформирован с ожидаемым контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        self.assertIsInstance(
            form.fields.get('text'), forms.fields.CharField)
        self.assertIsInstance(
            form.fields.get('group'), forms.fields.ChoiceField)
        self.assertContains(response, 'Новый пост')
        self.assertFalse(
            response.context['is_edit'], 'Переменная is_edit вернула True!'
        )

    def test_post_edit_page_show_correct_context(self):
        """Шаблон формы редактирования поста сформирован с ожидаемым
        контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        self.assertContains(response, 'Редактировать запись')

    def test_form_at_post_edit_page_contains_data(self):
        """Проверка содержания данных для изменения в форме редактирования
        поста."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form = response.context['form']
        self.assertEqual(form.initial['text'], self.post.text)

    def test_new_post_is_on_expected_pages(self):
        """Проверка доступности нового поста на индексе, странице группы и
        в профайле автора."""
        self.post = Post.objects.create(
            author=self.user,
            text='New test post',
            group=Group.objects.get(pk=1)
        )
        # Test profile
        response_profile = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        first_object = response_profile.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        # Test index
        cache.clear()
        response_index = self.authorized_client.get(
            reverse('posts:index'))
        first_object = response_index.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        # Test group Тестовая группа
        response_group_1 = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': Group.objects.get(pk=1).slug})
        )
        first_object = response_group_1.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)
        # Test group Тестовая группа №2
        response_group_2 = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response_group_2.context['page_obj'][0]
        self.assertNotEqual(first_object.text, self.post.text)

    def test_form_at_post_edit_page_updates_data(self):
        """Проверка изменения данных в записях при отправке формы
        на странице редактирования поста."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form = response.context['form']
        data = form.initial
        data['text'] = 'Post has been changed'
        if not data['group']:
            data['group'] = ''
        if not data['image']:
            data['image'] = ''
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}), data
        )
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context.get('post').text, 'Post has been changed'
        )

    def test_form_class_at_page_edit_page_is_PostForm(self):
        """Проверим, что форма редактирования поста является наследником
        класса PostForm."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            response.context['form'].__class__.__name__,
            'PostForm',
        )

    def test_post_edit_page_context_consists_is_edit(self):
        """Проверим, есть ли переменная is_edit в контексте страницы
        post_edit."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertTrue(
            response.context['is_edit'], 'Переменная is_edit вернула False!'
        )


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа №2',
            slug='test-group-slug',
            description='Тестовое описание №2',
        )
        for i in range(randrange(11, 20)):
            cls.post = Post.objects.create(
                author=cls.user,
                text=(f'Any text{i}'),
                group=Group.objects.get(pk=2)
            )

    def setUp(self):
        self.guest_client = Client()

    def posts_qty(self, page_number=1):
        if page_number == 1:
            return settings.POSTS_PER_PAGE
        else:
            return self.user.posts.all().count() - settings.POSTS_PER_PAGE

    def test_first_page_index_cotains_ten_records(self):
        """Проверка паджинатора index: 1 страница содержит 10 постов."""
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']), self.posts_qty())

    def test_second_page_index_cotains_four_records(self):
        """Проверка паджинатора index: 2 страница содержит от 1 до 9 постов."""
        cache.clear()
        response = self.guest_client.get(
            reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), self.posts_qty(2))

    def test_first_page_group_cotains_ten_records(self):
        """Проверка паджинатора group_list: 1 страница содержит 10 постов."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'})
        )
        self.assertEqual(
            len(response.context['page_obj']), self.posts_qty())

    def test_second_page_group_cotains_three_records(self):
        """Проверка паджинатора group_list: 2 страница содержит
        от 1 до 9 постов."""
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': f'{self.group.slug}'}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), self.posts_qty(2))

    def test_first_page_profile_cotains_ten_records(self):
        """Проверка паджинатора profile: 1 страница содержит 10 постов."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        self.assertEqual(
            len(response.context['page_obj']), self.posts_qty())

    def test_second_page_profile_cotains_four_records(self):
        """Проверка паджинатора profile: 2 страница содержит
        от 1 до 9 постов."""
        response = self.guest_client.get(
            reverse(
                'posts:profile', kwargs={'username': self.user}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), self.posts_qty(2))

    def test_first_pages_contain_10_records(self):
        """Проверка паджинатора первые страницы содержат 10 постов."""
        cache.clear()
        page_addresses = [
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user}/',
        ]
        for address in page_addresses:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(
                    len(response.context['page_obj']), self.posts_qty())


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='NoName')
        cls.post = Post.objects.create(
            author=cls.user,
            text=(f'Any text'),
        )

    def setUp(self):
        self.guest_client = Client()

    def test_cache_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом с учетом
        кеширования страницы на 20 секунд."""
        response_1 = self.guest_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_2 = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(response_1.content, response_2.content)
        cache.clear()
        response_3 = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(response_1.content, response_3.content)


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_follower = User.objects.create_user(username='NoName')
        cls.user_following = User.objects.create_user(username='AnyName')
        cls.post = Post.objects.create(
            author=cls.user_following,
            text='Тестовый текст',
        )

    def setUp(self):
        self.following_client = Client()
        self.follower_client = Client()
        self.following_client.force_login(self.user_following)
        self.follower_client.force_login(self.user_follower)

    def test_registered_user_can_follow(self):
        """Зарегистрированный пользователь может подписаться."""
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_follow',
            args=(self.user_following.username,)
        ))
        self.assertEqual(Follow.objects.count(), follower_count + 1)

    def test_registered_user_can_unfollow(self):
        """Зарегистрированный пользователь может отписаться."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        follower_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            args=(self.user_following.username,)
        ))
        self.assertEqual(Follow.objects.count(), follower_count - 1)

    def test_new_post_is_on_follow_page(self):
        """Новый пост появляется в ленте подписавшихся."""
        Follow.objects.create(
            user=self.user_follower,
            author=self.user_following
        )
        posts_count_before = Post.objects.select_related('author').filter(
            author__following__user=self.user_follower
        ).count()
        new_post = Post.objects.create(
            author=self.user_following,
            text='Post is written by following_client',
        )
        posts = Post.objects.select_related('author').filter(
            author__following__user=self.user_follower
        )
        self.assertTrue(posts.filter(text__contains=new_post.text).exists())
        self.assertEqual(posts.count(), posts_count_before + 1)
