
from unittest.mock import patch

import jwt
from django.conf import settings
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi_app.main import app, get_db
from fastapi_app.models import Base


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_test_token(user_id=1):
    return jwt.encode(
        {"user_id": user_id},
        settings.SECRET_KEY,
        algorithm="HS256",
    )


class TestPaymentAPI:

    def setup_method(self):
        Base.metadata.create_all(bind=test_engine)
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.headers = {
            "Authorization": f"Bearer {create_test_token(1)}"
        }

    def teardown_method(self):
        self.client.close()
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)

    def test_home_endpoint(self):
        response = self.client.get("/")

        assert response.status_code == 200
        assert response.json() == {
            "message": "Payment service is running"
        }

    def test_payment_requires_authentication(self):
        response = self.client.post(
            "/payments/",
            json={"card_id": 1, "amount": 100},
        )

        assert response.status_code == 401

    @patch(
        "fastapi_app.main.random.choice",
        return_value="SUCCESS",
    )
    @patch(
        "fastapi_app.main.find_user_card",
        return_value=(1,),
    )
    def test_successful_payment(self, mock_card, mock_choice):
        response = self.client.post(
            "/payments/",
            headers=self.headers,
            json={"card_id": 1, "amount": 500},
        )

        assert response.status_code == 200

        data = response.json()

        assert data["message"] == "Payment processed"
        assert data["amount"] == 500
        assert data["initial_status"] == "PENDING"
        assert data["final_status"] == "SUCCESS"
        assert data["transaction_id"] is not None

    @patch(
        "fastapi_app.main.random.choice",
        return_value="FAILED",
    )
    @patch(
        "fastapi_app.main.find_user_card",
        return_value=(1,),
    )
    def test_failed_payment(self, mock_card, mock_choice):
        response = self.client.post(
            "/payments/",
            headers=self.headers,
            json={"card_id": 1, "amount": 250},
        )

        assert response.status_code == 200
        assert response.json()["final_status"] == "FAILED"
        assert response.json()["transaction_id"] is not None

    @patch(
        "fastapi_app.main.find_user_card",
        return_value=None,
    )
    def test_card_not_found(self, mock_card):
        response = self.client.post(
            "/payments/",
            headers=self.headers,
            json={"card_id": 999, "amount": 100},
        )

        assert response.status_code == 404

    def test_zero_amount_rejected(self):
        response = self.client.post(
            "/payments/",
            headers=self.headers,
            json={"card_id": 1, "amount": 0},
        )

        assert response.status_code == 422

    def test_negative_amount_rejected(self):
        response = self.client.post(
            "/payments/",
            headers=self.headers,
            json={"card_id": 1, "amount": -100},
        )

        assert response.status_code == 422