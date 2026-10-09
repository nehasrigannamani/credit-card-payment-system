
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from cards.models import Card
from .models import Transaction


User = get_user_model()


class TransactionHistoryTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="transactionuser",
            email="transactionuser@example.com",
            password="TestPass123!",
        )

        login_response = self.client.post(
            "/api/users/login/",
            {
                "username": "transactionuser",
                "password": "TestPass123!",
            },
            format="json",
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {login_response.data['access']}"
            )
        )

        self.card = Card.objects.create(
            user=self.user,
            card_type="CREDIT",
            cardholder_name="Test User",
            masked_card_number="****-****-****-1234",
            last_four_digits="1234",
            expiry_date="2030-12-31",
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount="500.00",
            status="SUCCESS",
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount="1000.00",
            status="FAILED",
        )

    def test_transaction_history(self):
        response = self.client.get("/api/transactions/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_status(self):
        response = self.client.get(
            "/api/transactions/?status=SUCCESS"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "SUCCESS")

    def test_filter_by_minimum_amount(self):
        response = self.client.get(
            "/api/transactions/?min_amount=600"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_maximum_amount(self):
        response = self.client.get(
            "/api/transactions/?max_amount=600"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_transaction_history_without_authentication(self):
        self.client.credentials()

        response = self.client.get("/api/transactions/")

        self.assertEqual(response.status_code, 401)