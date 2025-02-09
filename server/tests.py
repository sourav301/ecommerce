from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token

class UserAuthTestCase(APITestCase):

    def setUp(self):
        """
        Set up test data: Create a test user.
        """
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.register_url = reverse("register")  # Replace with actual registration URL name
        self.login_url = reverse("login")  # Replace with actual login URL name

    def test_user_registration(self):
        """
        Ensure that a user can register successfully.
        """
        data = {
            "username": "newuser",
            "password": "newpass",
            "email": "newuser@example.com",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_login(self):
        """
        Ensure that a user can log in and receive a token.
        """
        data = {
            "username": "testuser",
            "password": "testpass",
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)  # Token should be in response