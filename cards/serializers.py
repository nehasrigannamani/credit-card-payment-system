from rest_framework import serializers

from .models import Card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = [
            "id",
            "card_type",
            "cardholder_name",
            "masked_card_number",
            "last_four_digits",
            "expiry_date",
        ]
        read_only_fields = ["id"]