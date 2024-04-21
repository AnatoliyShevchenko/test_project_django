# Simple JWT
from rest_framework_simplejwt.views import TokenRefreshView

# Rest Framework
from rest_framework.routers import DefaultRouter

# Django
from django.contrib import admin
from django.urls import path, include

# Local
from auths.views import CustomAuth, PersonalArea


router = DefaultRouter(trailing_slash=True)
# router.register("auths", CustomAuth)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path("api/v1/auths/", CustomAuth.as_view()),
    path("api/v1/personal-area/", PersonalArea.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
