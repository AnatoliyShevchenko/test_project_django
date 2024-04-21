# Rest Framework
from rest_framework import serializers

# Third-Party
from phonenumber_field.serializerfields import PhoneNumberField

# Local
from .models import Client


class PhoneNumberSerializer(serializers.Serializer):
    """Serializer for phone numbers."""

    phone_number = PhoneNumberField()


class OTPSerializer(serializers.Serializer):
    """Serializer for OTP."""

    otp = serializers.CharField(min_length=4, max_length=4)


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for get information about clients."""

    followers = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = (
            "phone_number", "invite_code", "invited_by", "followers"
        )

    def get_followers(self, obj: Client):
        data = Client.objects.filter(
            invited_by__invite_code=obj.invite_code
        )
        serializer = PhoneNumberSerializer(data=data, many=True)
        serializer.is_valid()
        return serializer.data
    

class InviteSerializer(serializers.Serializer):
    """Serializer for invite codes."""
    
    invited_by = serializers.CharField(min_length=6, max_length=6)

