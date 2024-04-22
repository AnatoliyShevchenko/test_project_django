# Simple JWT
from rest_framework_simplejwt.views import TokenRefreshView

# Rest Framework
from rest_framework.routers import DefaultRouter

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Django
from django.contrib import admin
from django.urls import path, include

# Local
from auths.views import CustomAuth, PersonalArea


router = DefaultRouter(trailing_slash=True)
# router.register("auths", CustomAuth)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls")),
    path("api/v1/auths/", CustomAuth.as_view(), name="custom-auth"),
    path("api/v1/personal-area/", PersonalArea.as_view(), 
        name="personal-area"),
    path("api/token/refresh/", TokenRefreshView.as_view(), 
        name="token_refresh"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger-ui/", SpectacularSwaggerView.as_view(
        url_name="schema"
    ), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(
        url_name="schema"
    ), name="redoc"),
]
