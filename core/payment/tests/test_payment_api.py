import pytest
from django.urls import reverse
from rest_framework import status
from order.models import OrderModel  

pytestmark = pytest.mark.django_db

class TestPaymentAPI:
    def test_create_payment(self, authenticated_client):
        client, user = authenticated_client
        order = OrderModel.objects.create(
            user=user,
            first_name="Test",
            last_name="User",
            phone_number="0912",
            address="Test Addr",
            total_price=100000
        )

        url = reverse('payment:payment-list')  # check your router name
        data = {"order": order.id, "amount": 100000}
        response = client.post(url, data, format='json')

        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]