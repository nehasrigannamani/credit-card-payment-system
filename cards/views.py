from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CardSerializer
from .models import Card

class CardListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cards = Card.objects.filter(user=request.user)

        serializer = CardSerializer(cards, many=True)

        return Response(serializer.data)

class CardDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, card_id):
        try:
            card = Card.objects.get(
                id=card_id,
                user=request.user
            )
        except Card.DoesNotExist:
            return Response(
                {"message": "Card not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        card.delete()

        return Response(
            {"message": "Card deleted successfully"},
            status=status.HTTP_200_OK
        )


class CardCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CardSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )