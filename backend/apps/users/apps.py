from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration for the user management application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
