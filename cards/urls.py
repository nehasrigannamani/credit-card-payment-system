from django.urls import path

from .views import CardCreateView, CardListView, CardDeleteView


urlpatterns = [
    path("add/", CardCreateView.as_view(), name="add-card"),
    path("", CardListView.as_view(), name="card-list"),
    path("<int:card_id>/", CardDeleteView.as_view(), name="card-delete"),
]