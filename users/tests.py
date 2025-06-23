from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from users.models import Profile
from PIL import Image
import tempfile
import os
from django.core import mail
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm


class ProfileModelTests(TestCase):
    """Тесты для модели Profile"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        # Profile должен создаваться автоматически через сигналы
        self.profile = Profile.objects.get(user=self.user)
        
    def test_profile_creation(self):
        """Тест создания профиля"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.avatar, 'default.jpg')
        self.assertEqual(self.profile.bio, '')
        self.assertEqual(self.profile.position, '')
        self.assertEqual(self.profile.phone, '')
        
    def test_profile_str(self):
        """Тест строкового представления профиля"""
        self.assertEqual(str(self.profile), f'Профиль пользователя {self.user.username}')


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }

    def test_register_view(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/register.html')

    def test_register_success(self):
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='testuser').exists())
        self.assertEqual(len(mail.outbox), 1)  # Check if confirmation email was sent

    def test_register_invalid_data(self):
        # Test with mismatched passwords
        data = self.valid_data.copy()
        data['password2'] = 'differentpass'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertFormError(response, 'form', 'password2', 'The two password fields didn\'t match.')

        # Test with existing username
        User.objects.create_user(username='testuser', password='testpass123')
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'A user with that username already exists.')


class UserLoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_login_view(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, 'Please enter a correct username and password.')


class UserProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile_url = reverse('profile')
        self.client.login(username='testuser', password='testpass123')

    def test_profile_view(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_profile_update(self):
        response = self.client.post(self.profile_url, {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')


class UserFormTest(TestCase):
    def test_user_register_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test invalid data
        form_data['password2'] = 'differentpass'
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_user_update_form(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        form_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Updated',
            'last_name': 'User'
        }
        form = UserUpdateForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())

    def test_profile_update_form(self):
        user = User.objects.create_user(username='testuser')
        form_data = {
            'bio': 'Test bio',
            'location': 'Test location'
        }
        form = ProfileUpdateForm(data=form_data, instance=user.profile)
        self.assertTrue(form.is_valid())
