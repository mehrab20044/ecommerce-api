import pytest
from django.urls import reverse
from rest_framework import status
from catalog.models import Category, Product
from order.models import OrderItemModel, OrderModel
from payment.models import PaymentModel, PaymentStatus

pytestmark = pytest.mark.django_db


class ZarinpalResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class TestPaymentAPI:
    def test_create_payment(self, authenticated_client, monkeypatch):
        client, user = authenticated_client
        category = Category.objects.create(title="Test", slug="payment-test")
        product = Product.objects.create(
            category=category,
            title="Payment Product",
            slug="payment-product",
            description="Test product",
            price=100000,
            stock=10,
            status=1,
        )
        order = OrderModel.objects.create(
            user=user,
            first_name="Test",
            last_name="User",
            phone_number="0912",
            address="Test Addr",
        )
        OrderItemModel.objects.create(
            order=order,
            product=product,
            product_title=product.title,
            product_price=product.price,
            quantity=1,
        )

        def fake_zarinpal_request(*args, **kwargs):
            return ZarinpalResponse({
                "data": {
                    "authority": "S000000000000000000000000000000TEST",
                    "code": 100,
                    "message": "Success",
                },
                "errors": [],
            })

        monkeypatch.setattr("payment.api.v1.views.requests.post", fake_zarinpal_request)

        url = reverse('payment:payments-list')
        data = {"order_id": order.id}
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["payment_url"].endswith("S000000000000000000000000000000TEST")

        payment = PaymentModel.objects.get(id=response.data["payment_id"])
        assert payment.status == PaymentStatus.PENDING
        assert payment.authority == "S000000000000000000000000000000TEST"

    def test_create_payment_returns_zarinpal_error_without_500(self, authenticated_client, monkeypatch):
        client, user = authenticated_client
        category = Category.objects.create(title="Error Test", slug="payment-error-test")
        product = Product.objects.create(
            category=category,
            title="Payment Error Product",
            slug="payment-error-product",
            description="Test product",
            price=100000,
            stock=10,
            status=1,
        )
        order = OrderModel.objects.create(
            user=user,
            first_name="Test",
            last_name="User",
            phone_number="0912",
            address="Test Addr",
        )
        OrderItemModel.objects.create(
            order=order,
            product=product,
            product_title=product.title,
            product_price=product.price,
            quantity=1,
        )

        def fake_zarinpal_error(*args, **kwargs):
            return ZarinpalResponse({
                "errors": {
                    "code": -9,
                    "message": "Invalid payment request",
                }
            })

        monkeypatch.setattr("payment.api.v1.views.requests.post", fake_zarinpal_error)

        response = client.post(
            reverse('payment:payments-list'),
            {"order_id": order.id},
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["error"]["code"] == -9

        payment = PaymentModel.objects.get(order=order)
        assert payment.status == PaymentStatus.FAILED
