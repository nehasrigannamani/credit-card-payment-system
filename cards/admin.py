
from django.contrib import admin

from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "card_type",
        "cardholder_name",
        "masked_card_number",
        "expiry_date",
    )

    search_fields = (
        "user__username",
        "cardholder_name",
        "last_four_digits",
    )

    list_filter = (
        "card_type",
        "expiry_date",
    )