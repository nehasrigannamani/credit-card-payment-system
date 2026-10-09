from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/cards/", include("cards.urls")),
    path("api/transactions/", include("transactions.urls")),
]