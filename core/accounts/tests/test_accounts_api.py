import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import User

pytestmark = pytest.mark.django_db

class TestRegistration:
    def test_register_success(self, api_client):
        url = reverse('accounts:register')  # accounts/api/v1/urls.py
        data = {
            "email": "newuser@example.com",
            "password": "StrongPass123!",
            "first_name": "NewUser"
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert "email" in response.data

    def test_register_duplicate_email(self, api_client, create_user):
        create_user(email="duplicate@example.com")
        url = reverse('accounts:register')
        data = {"email": "duplicate@example.com", "password": "pass123"}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestJWT:
    def test_obtain_token(self, api_client, create_user):
        user = create_user()
        url = reverse('accounts:create')  # jwt/create
        data = {"email": user.email, "password": "testpass123"}
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data


class TestProfile:
    def test_get_profile(self, authenticated_client):
        client, user = authenticated_client
        url = reverse('accounts:profile')
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user']['email'] == user.email