from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.views.auth_views import RegistrationView

urlpatterns = [
    path("register", RegistrationView.as_view(), name="register"),
    path("tokens", TokenObtainPairView.as_view(), name="get-tokens"),
    path("tokens/refresh", TokenRefreshView.as_view(), name="refresh-tokens"),
]
