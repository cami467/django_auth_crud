from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationViewsTests(TestCase):
    def test_signup_creates_user_and_redirects(self):
        response = self.client.post(reverse('signup'), {
            'username': 'camila',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })

        self.assertRedirects(response, reverse('tasks'))
        self.assertTrue(User.objects.filter(username='camila').exists())

    def test_signup_with_invalid_data_returns_400(self):
        response = self.client.post(reverse('signup'), {
            'username': 'camila',
            'password1': '123',
            'password2': '456',
        })

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'No se pudo crear el usuario', status_code=400)

    def test_signin_with_invalid_credentials_returns_400(self):
        User.objects.create_user(username='camila', password='StrongPass123')

        response = self.client.post(reverse('signin'), {
            'username': 'camila',
            'password': 'incorrecta',
        })

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Usuario o contraseña incorrecta', status_code=400)

    def test_tasks_completed_page_loads_for_authenticated_user(self):
        user = User.objects.create_user(username='camila', password='StrongPass123')
        self.client.force_login(user)

        response = self.client.get(reverse('tasks_completed'))

        self.assertEqual(response.status_code, 200)
