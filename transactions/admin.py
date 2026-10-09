
import csv
from datetime import date

from django.contrib import admin
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path

from admin_logs.models import AdminLog
from .models import Transaction


def export_transactions_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="transactions.csv"'
    )

    writer = csv.writer(response)
    writer.writerow([
        "ID",
        "Username",
        "Card ID",
        "Amount",
        "Status",
        "Created At",
    ])

    for transaction in queryset:
        writer.writerow([
            transaction.id,
            transaction.user.username,
            transaction.card.id,
            transaction.amount,
            transaction.status,
            transaction.created_at,
        ])

    AdminLog.objects.create(
        admin_user=request.user,
        action="EXPORT",
        description="Exported selected transactions to CSV.",
    )

    return response


export_transactions_csv.short_description = (
    "Export selected transactions to CSV"
)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "card",
        "amount",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    actions = [export_transactions_csv]

    def save_model(self, request, obj, form, change):
        action = "UPDATE" if change else "CREATE"

        super().save_model(request, obj, form, change)

        AdminLog.objects.create(
            admin_user=request.user,
            action=action,
            description=(
                f"Transaction {obj.id} was {action.lower()}d."
            ),
        )

    def delete_model(self, request, obj):
        transaction_id = obj.id

        super().delete_model(request, obj)

        AdminLog.objects.create(
            admin_user=request.user,
            action="DELETE",
            description=f"Transaction {transaction_id} was deleted.",
        )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "daily-summary/",
                self.admin_site.admin_view(self.daily_summary),
                name="transaction-daily-summary",
            ),
        ]

        return custom_urls + urls

    def daily_summary(self, request):
        today = date.today()

        transactions = Transaction.objects.filter(
            created_at__date=today
        )

        summary = transactions.aggregate(
            total_payments=Count("id"),
            successful_payments=Count(
                "id",
                filter=Q(status="SUCCESS"),
            ),
            failed_payments=Count(
                "id",
                filter=Q(status="FAILED"),
            ),
            successful_amount=Sum(
                "amount",
                filter=Q(status="SUCCESS"),
            ),
        )

        context = {
            **self.admin_site.each_context(request),
            "title": "Daily Payment Summary",
            "today": today,
            "summary": summary,
        }

        return TemplateResponse(
            request,
            "admin/daily_summary.html",
            context,
        )