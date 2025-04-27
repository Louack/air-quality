from apps.users.serializers.auth_serializers import RegistrationSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny


class RegistrationView(generics.CreateAPIView):
    """
    Provides an endpoint for user registration.
    """

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
