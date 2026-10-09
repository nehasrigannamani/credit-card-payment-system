
import os
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
from dotenv import load_dotenv

load_dotenv()
django.setup()

import jwt
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from django.conf import settings

from fastapi_app.database import SessionLocal
from fastapi_app.models import Transaction


app = FastAPI(title="Credit Card Payment API")

security = HTTPBearer()


class PaymentRequest(BaseModel):
    card_id: int
    amount: float = Field(gt=0)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
            )

        return int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
        )


def find_user_card(db: Session, card_id: int, user_id: int):
    return db.execute(
        text("""
            SELECT id
            FROM cards_card
            WHERE id = :card_id AND user_id = :user_id
        """),
        {
            "card_id": card_id,
            "user_id": user_id,
        },
    ).fetchone()


@app.get("/")
def home():
    return {"message": "Payment service is running"}


@app.post("/payments/")
def make_payment(
    payment: PaymentRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    card = find_user_card(
        db,
        payment.card_id,
        user_id,
    )

    if card is None:
        raise HTTPException(
            status_code=404,
            detail="Card not found for this user",
        )

    payment_result = random.choice(["SUCCESS", "FAILED"])

    transaction = Transaction(
        user_id=user_id,
        card_id=payment.card_id,
        amount=payment.amount,
        status=payment_result,
    )

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to record payment",
        )

    return {
        "message": "Payment processed",
        "transaction_id": transaction.id,
        "user_id": user_id,
        "card_id": payment.card_id,
        "amount": payment.amount,
        "initial_status": "PENDING",
        "final_status": payment_result,
    }