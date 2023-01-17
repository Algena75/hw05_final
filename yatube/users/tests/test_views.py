from django.test import Client, TestCase
from django.urls import reverse


class UserViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_form_class_at_page_edit_page_is_PostForm(self):
        """Проверим, что форма редактирования поста является наследником
        класса PostForm."""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertEqual(
            response.context['form'].__class__.__name__,
            'CreationForm',
        )
