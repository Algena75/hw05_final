from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='NoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_exist_at_desired_location(self):
        """Общедоступные страницы доступны по ожидаемому адресу."""
        pages_address = [
            'users:signup',
            'users:login',
            'users:password_reset',
            'users:password_reset_done',
            'users:password_reset_complete',
        ]
        for address in pages_address:
            with self.subTest(address=address):
                response = self.guest_client.get(reverse(address))
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_login_required_pages_exist_at_desired_location(self):
        """Страницы, требующие авторизации, доступны по ожидаемому адресу."""
        pages_address = [
            'users:password_change',
            'users:password_change_done',
            'users:logout',
        ]
        for address in pages_address:
            with self.subTest(address=address):
                response = self.authorized_client.get(reverse(address))
                self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_password_reset_confirm_page_exists_at_desired_location(self):
        """Страница подтверждения сброса пароля доступна по ожидаемому
        адресу."""
        response = self.guest_client.get(
            reverse(
                'users:password_reset_confirm',
                args=['<uidb64>', '<token>'],
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
