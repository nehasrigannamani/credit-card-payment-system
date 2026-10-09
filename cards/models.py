from django.conf import settings
from django.db import models


class Card(models.Model):
    CARD_TYPES = [
        ("CREDIT", "Credit"),
        ("DEBIT", "Debit"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    card_type = models.CharField(
        max_length=10,
        choices=CARD_TYPES
    )
    cardholder_name = models.CharField(max_length=100)
    masked_card_number = models.CharField(max_length=19)
    last_four_digits = models.CharField(max_length=4)
    expiry_date = models.DateField()

    def __str__(self):
        return f"{self.card_type} ****{self.last_four_digits}"