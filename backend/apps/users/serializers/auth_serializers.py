from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Handles the validation and creation of new user accounts.
    """

    password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )

    password2 = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ("username", "password", "password2")

    def save(self, **kwargs):
        """
        Creates a new user account with the provided credentials.
        """
        new_user = User(username=self.validated_data["username"])
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError(
                {"Password": "Passwords are not matching."}
            )

        new_user.set_password(password)
        new_user.save()
