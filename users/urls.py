from django.urls import path

from .views import RegisterView, ProfileView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("logout/", TokenBlacklistView.as_view(), name="logout"),
]