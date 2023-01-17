from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticURLTests(TestCase):
    def test_static_about_pages_exist_at_desired_location(self):
        """Статические страницы приложения about доступны по ожидаемым
        адресам."""
        guest_client = Client()
        pages_address = [
            'about:author',
            'about:tech',
        ]
        for address in pages_address:
            with self.subTest(address=address):
                response = guest_client.get(reverse(address))
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
