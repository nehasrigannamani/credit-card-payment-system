from sqlalchemy import Column, Integer, Numeric, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime


Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions_transaction"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    card_id = Column(Integer)
    amount = Column(Numeric(10, 2))
    status = Column(String(10))
    created_at = Column(DateTime, default=datetime.now)