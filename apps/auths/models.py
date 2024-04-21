# Django
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import (
    PermissionsMixin, AbstractBaseUser,
)
from django.db import models
from django.core.exceptions import ValidationError
from django.core.cache import cache

# Third-Party
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from phonenumber_field.validators import to_python

# Python
import secrets
import string
import random
import logging


logger = logging.getLogger(__name__)


class ClientManager(BaseUserManager):
    """Custom class for User Manager."""

    def generate_otp(self):
        """
        Generate a random OTP (One-Time Password).
        
        :return: A randomly generated OTP.
        :rtype: str
        """
        while True:
            otp = ""
            while len(otp) < 4:
                otp += str(random.randint(0,9))
            client = cache.get(key=f"{otp}_client")
            if not client:
                return otp

    def generate_invite_code(self, count_symbols: int = 6):
        """
        Generate a random invite code.

        :param count_symbols: The number of symbols in the generated code (default is 6).
        :type count_symbols: int
        :return: A randomly generated invite code.
        :rtype: str
        """
        alphabet = string.ascii_letters + string.digits
        while True:
            code = ''.join(
                secrets.choice(alphabet) for _ in range(count_symbols)
            )
            if not self.model.objects.filter(
                invite_code=code
            ).exists():
                logger.info(msg=f"CODE: {code}")
                return code

    def create_user(self, phone_number: str) -> "Client":
        """
        Create a new client user.

        :param phone_number: The phone number of the client user.
        :type phone_number: str
        :raises ValidationError: If the phone number is not provided or is not correct.
        :return: The newly created client user.
        :rtype: Client
        """
        if not phone_number:
            raise ValidationError(message="Phone number required")
        phone = to_python(value=phone_number)
        if not isinstance(phone, PhoneNumber):
            raise ValidationError(
                message="Phone number is not correct"
            )

        user: "Client" = self.model(phone_number=phone,)
        user.invite_code = self.generate_invite_code()
        user.save()
        return user
    
    def create_superuser(
        self, phone_number: str, password: str
    ) -> "Client":
        """
        Create a new superuser client.

        :param phone_number: The phone number of the superuser client.
        :type phone_number: str
        :param password: The password for the superuser client.
        :type password: str
        :raises ValidationError: If the phone number is not provided or is not correct.
        :return: The newly created superuser client.
        :rtype: Client
        """
        if not phone_number:
            raise ValidationError(message="Phone number required")
        phone = to_python(value=phone_number)
        if not isinstance(phone, PhoneNumber):
            raise ValidationError(message="Phone number is not correct")
        user: "Client" = self.model(phone_number=phone,)
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.set_password(password)
        user.save()
        return user


class Client(AbstractBaseUser, PermissionsMixin):
    """Custom class for users."""

    phone_number = PhoneNumberField(
        verbose_name="номер телефона", unique=True,
    )
    is_active = models.BooleanField(
        default=False, verbose_name="активный"
    )
    is_staff = models.BooleanField(
        default=False, verbose_name="менеджер"
    )
    is_superuser = models.BooleanField(
        default=False, verbose_name="администратор"
    )
    password = models.CharField(
        verbose_name="пароль", max_length=128, null=True, blank=True
    )
    invite_code = models.CharField(
        verbose_name="код приглашения", unique=True, max_length=6,
        null=True, blank=True
    )
    invited_by = models.ForeignKey(
        to="Client", on_delete=models.CASCADE,
        null=True, blank=True
    )

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    objects = ClientManager()

    class Meta:
        ordering = ("id",)
        verbose_name = "клиент"
        verbose_name_plural = "клиенты"

    def __str__(self) -> str:
        return f"{self.phone_number}"
    
