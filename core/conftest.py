import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test"
    )
    api_client.force_authenticate(user=user)
    return api_client, user