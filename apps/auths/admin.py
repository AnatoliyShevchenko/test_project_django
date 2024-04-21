# Django
from django.contrib import admin

# Local
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Admin panel for custom user's class."""

    model = Client
    list_display = (
        "phone_number", "is_superuser", "invite_code", 
        "invited_by", "is_staff", "is_active"
    )
    list_filter = ("phone_number", "invite_code", "invited_by")
    search_fields = ("phone_number", "invite_code", "invited_by")

