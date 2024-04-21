# Rest Framework
from rest_framework import serializers

# Third-Party
from phonenumber_field.serializerfields import PhoneNumberField

# Python
import re

# Local
from .models import Client


class PhoneNumberSerializer(serializers.Serializer):
    """Serializer for phone numbers."""

    phone_number = PhoneNumberField()


def validate_otp(value):
    """
    Валидатор для поля otp.

    :param value: Значение поля otp.
    :type value: str
    :return: Отформатированное значение поля otp или вызывает исключение ValidationError, если значение недопустимо.
    :rtype: str
    """
    # Проверяем, что значение состоит только из цифр
    if not re.match("^\d{4}$", value):
        raise serializers.ValidationError("OTP должен состоять только из цифр.")
    
    return value

class OTPSerializer(serializers.Serializer):
    """Serializer for OTP."""

    otp = serializers.CharField(
        min_length=4, max_length=4, validators=[validate_otp]
    )


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

