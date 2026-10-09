
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


User = get_user_model()


class UserTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        data = {
            "username": "testuser123",
            "email": "testuser123@example.com",
            "password": "TestPass123!",
        }

        response = self.client.post(
            "/api/users/register/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_user_login(self):
        User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="TestPass123!",
        )

        response = self.client.post(
            "/api/users/login/",
            {
                "username": "loginuser",
                "password": "TestPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_with_authentication(self):
        user = User.objects.create_user(
            username="profileuser",
            email="profileuser@example.com",
            password="TestPass123!",
        )

        login_response = self.client.post(
            "/api/users/login/",
            {
                "username": "profileuser",
                "password": "TestPass123!",
            },
            format="json",
        )

        access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        response = self.client.get("/api/users/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["username"],
            user.username,
        )
        self.assertEqual(
            response.data["email"],
            user.email,
        )

    def test_profile_without_authentication(self):
        response = self.client.get("/api/users/profile/")

        self.assertEqual(response.status_code, 401)