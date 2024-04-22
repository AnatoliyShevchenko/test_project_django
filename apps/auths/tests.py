# Rest Framework
from rest_framework.test import APIClient
from rest_framework import status

# Django
from django.test import TestCase
from django.urls import reverse


class TestCustomAuth(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.correct_phone_number = "+77777777777"
        self.incorrect_phone_number = "1349745317454154"

    def test_get_method(self):
        url = reverse("custom-auth")
        response = self.client.get(url)
        self.assertEqual(
            first=response.status_code, 
            second=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_correct_post_method(self):
        url = reverse("custom-auth")
        data = {"phone_number": self.correct_phone_number}
        response = self.client.post(url, data)
        self.assertEqual(
            first=response.status_code, second=status.HTTP_200_OK
        )
        self.assertIn("response", response.data)

    def test_incorrect_post_method(self):
        url = reverse("custom-auth")
        data = {"phone_number": self.incorrect_phone_number}
        response = self.client.post(url, data)
        self.assertEqual(
            first=response.status_code, 
            second=status.HTTP_400_BAD_REQUEST
        )
        self.assertIn("phone_number", response.data)


