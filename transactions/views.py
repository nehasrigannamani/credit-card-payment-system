from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        transactions = Transaction.objects.filter(
            user=request.user
        )

        # Filter by status
        status_filter = request.query_params.get("status")

        if status_filter:
            transactions = transactions.filter(
                status=status_filter.upper()
            )

        # Filter by minimum amount
        min_amount = request.query_params.get("min_amount")

        if min_amount:
            transactions = transactions.filter(
                amount__gte=min_amount
            )

        # Filter by maximum amount
        max_amount = request.query_params.get("max_amount")

        if max_amount:
            transactions = transactions.filter(
                amount__lte=max_amount
            )

        # Filter by start date
        start_date = request.query_params.get("start_date")

        if start_date:
            transactions = transactions.filter(
                created_at__date__gte=start_date
            )

        # Filter by end date
        end_date = request.query_params.get("end_date")

        if end_date:
            transactions = transactions.filter(
                created_at__date__lte=end_date
            )

        # Show latest transactions first
        transactions = transactions.order_by("-created_at")

        serializer = TransactionSerializer(
            transactions,
            many=True
        )

        return Response(serializer.data)