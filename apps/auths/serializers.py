# Rest Framework
from rest_framework import serializers

# Third-Party
from phonenumber_field.serializerfields import PhoneNumberField

# Local
from .models import Client


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()


class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(min_length=4, max_length=4)


class ClientSerializer(serializers.ModelSerializer):
    
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
    invited_by = serializers.CharField(min_length=6, max_length=6)

