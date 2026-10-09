
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from .models import Card


User = get_user_model()


class CardAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="carduser",
            email="carduser@example.com",
            password="TestPass123!",
        )

        login_response = self.client.post(
            "/api/users/login/",
            {
                "username": "carduser",
                "password": "TestPass123!",
            },
            format="json",
        )

        self.access_token = login_response.data["access"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

        self.card_data = {
            "card_type": "CREDIT",
            "cardholder_name": "Test User",
            "masked_card_number": "****-****-****-1234",
            "last_four_digits": "1234",
            "expiry_date": "2030-12-31",
        }

    def test_create_card(self):
        response = self.client.post(
            "/api/cards/add/",
            self.card_data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["last_four_digits"],
            "1234",
        )

    def test_list_cards(self):
        Card.objects.create(
            user=self.user,
            **self.card_data,
        )

        response = self.client.get("/api/cards/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_delete_card(self):
        card = Card.objects.create(
            user=self.user,
            **self.card_data,
        )

        response = self.client.delete(
            f"/api/cards/{card.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Card.objects.filter(id=card.id).exists()
        )

    def test_card_list_without_authentication(self):
        self.client.credentials()

        response = self.client.get("/api/cards/")

        self.assertEqual(response.status_code, 401)