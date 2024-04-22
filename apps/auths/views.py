# Simple JWT
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication

# Rest Framework
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

# Django
from django.core.cache import cache

# Third-Party
from drf_spectacular.utils import extend_schema

# Python
import logging
import time

# Local
from .serializers import (
    PhoneNumberSerializer, OTPSerializer, ClientSerializer,
    InviteSerializer, SomeResponseSerializer,
    TokensSerializer,
)
from .models import Client


logger = logging.getLogger(__name__)


@permission_classes([AllowAny])
class CustomAuth(APIView):
    """
    Custom authorization with request phone number.
    This view handles authentication using a phone number.
    """

    def create_tokens(self, client: Client):
        """
        Create access and refresh tokens for the client user.

        :param client: The client user for whom tokens are created.
        :type client: Client
        :return: Dictionary containing access and refresh tokens.
        :rtype: dict
        """
        while True:
            try:
                access_token = AccessToken.for_user(client)
                refresh_token = RefreshToken.for_user(client)
                return {
                    "access_token":str(access_token),
                    "refresh_token":str(refresh_token)
                }
            except TokenError as e:
                logger.warning(msg=e)
                pass
    
    @extend_schema(
        description="Pass.",
        responses={405: SomeResponseSerializer}
    )
    def get(self, request: Request) -> Response:
        """
        Handle GET requests.

        :param request: The request object.
        :type request: Request
        :return: Response indicating that POST and PATCH methods should be used.
        :rtype: Response
        """
        serializer = SomeResponseSerializer(data={
            "response":"use POST and PATCH methods"
        })
        serializer.is_valid(raise_exception=True)
        return Response(
            status=status.HTTP_405_METHOD_NOT_ALLOWED, 
            data=serializer.data
        )

    @extend_schema(
        request=PhoneNumberSerializer,
        responses={200: SomeResponseSerializer},
    )
    def post(self, request: Request) -> Response:
        """
        Handle POST requests for phone number verification.

        :param request: The request object.
        :type request: Request
        :return: Response indicating that a confirmation code has been sent.
        :rtype: Response
        """
        serializer = PhoneNumberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get("phone_number")
        client, _ = Client.objects.get_or_create(
            phone_number=phone_number
        )
        otp = Client.objects.generate_otp()
        time.sleep(2.0)
        cache.set(key=f"{otp}_client", value=client, timeout=120)
        response = SomeResponseSerializer(data={
            "response":f"We will sent code to you in sms.(use {otp}), you have 2 minutes to confirm your number!"
        })
        response.is_valid(raise_exception=True)
        return Response(status=status.HTTP_200_OK, data=response.data)

    @extend_schema(
        request=OTPSerializer,
        responses={
            200: TokensSerializer,
            400: SomeResponseSerializer
        },
    )
    def patch(self, request: Request) -> Response:
        """
        Handle PATCH requests for OTP verification.

        :param request: The request object.
        :type request: Request
        :return: Response indicating successful authentication or failure.
        :rtype: Response
        """
        serializer = OTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data.get("otp")
        client: Client = cache.get(key=f"{otp}_client")
        if client:
            if not client.is_active:
                client.invite_code = Client.objects.generate_invite_code()
                client.is_active = True
                client.save(update_fields=("is_active", "invite_code"))
            
            pairs = self.create_tokens(client=client)
            cache.delete(key=f"{otp}_client")
            response = TokensSerializer(data=pairs)
            response.is_valid(raise_exception=True)
            return Response(status=status.HTTP_200_OK, data=response.data)
        
        logger.info(msg="User not found!")
        response = SomeResponseSerializer(data={
            "response": "Пользователь не найден, возможно вы ждали дольше 2 минут. Вернитесь на предыдущий шаг."
        })
        response.is_valid(raise_exception=True)
        return Response(
            data=response.data,
            status=status.HTTP_400_BAD_REQUEST
        )


@permission_classes([IsAuthenticated])
class PersonalArea(APIView):
    """
    View for manipulating data in the personal area.
    This view provides endpoints for accessing and modifying client data in the personal area.
    """

    authentication_classes = [JWTAuthentication]

    @extend_schema(responses={200:ClientSerializer})
    def get(self, request: Request) -> Response:
        """
        Handle GET requests to retrieve client data.

        :param request: The request object.
        :type request: Request
        :return: Response with client data.
        :rtype: Response
        """
        client: Client = request.user
        serializer = ClientSerializer(instance=client)
        data = serializer.data

        return Response(status=status.HTTP_200_OK, data=data)
    
    @extend_schema(
        request=InviteSerializer,
        responses={
            200:SomeResponseSerializer,
            400:SomeResponseSerializer
        }
    )
    def patch(self, request: Request) -> Response:
        """
        Handle PATCH requests to update inviter information.

        :param request: The request object.
        :type request: Request
        :return: Response indicating success or failure of updating inviter information.
        :rtype: Response
        """
        client: Client = request.user
        serializer = InviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invited_by = serializer.validated_data.get("invited_by")
        try:
            inviter = Client.objects.get(invite_code=invited_by)
            if client.invited_by:
                response = SomeResponseSerializer(data={
                    "response":"ERROR: you already have inviter!"
                })
                response.is_valid(raise_exception=True)
                return Response(
                    data=response.data, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif not client.invited_by:
                client.invited_by = inviter
                client.save(update_fields=("invited_by",))
                response = SomeResponseSerializer(data={
                    "response":"Inviter added!"
                })
                response.is_valid(raise_exception=True)
                return Response(
                    status=status.HTTP_200_OK, data=response.data
                )
        except Client.DoesNotExist:
            response = SomeResponseSerializer(data={
                "response":f"ERROR: the client with code: {invited_by} not found."
            })
            response.is_valid(raise_exception=True)
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data=response.data
            )

