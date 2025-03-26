from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Air Quality",
        default_version="v1",
    ),
    public=True,
    permission_classes=[
        AllowAny,
    ],
)

urlpatterns = [
    path("docs", schema_view.with_ui("swagger", cache_timeout=0), name="docs"),
    path("silk", include("silk.urls")),
    path("admin", admin.site.urls),
    path("auth/", include("apps.users.urls")),
    path("", include("apps.air_quality.urls")),
]
