from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='NoName')
        self.guest_client = Client()

    def test_signup_form_creates_new_user(self):
        """Проверка создания нового пользователя при отправке формы
        reverse('users:signup')."""
        users_count = User.objects.count()
        data = {
            'username': 'new_user',
            'password1': 'Fckn_idiot',
            'password2': 'Fckn_idiot',
        }
        self.guest_client.post(reverse('users:signup'), data)
        self.assertEqual(
            User.objects.count(),
            users_count + 1
        )
