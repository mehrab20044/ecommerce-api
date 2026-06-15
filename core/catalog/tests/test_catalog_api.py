import pytest
from django.urls import reverse
from rest_framework import status
from catalog.models import Category, Product

pytestmark = pytest.mark.django_db

class TestCategory:
    def test_list_categories(self, api_client):
        Category.objects.create(title="Electronics", slug="electronics")
        url = reverse('api-v1:category-list')   # router
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

class TestProduct:
    def test_list_products(self, api_client):
        cat = Category.objects.create(title="Test", slug="test")
        Product.objects.create(
            category=cat, title="Test Product", slug="test-prod",
            price=1000, stock=10, status=1
        )
        url = reverse('api-v1:product-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert any(p['title'] == "Test Product" for p in response.data['results'] if isinstance(response.data, dict))

    def test_product_detail(self, api_client):
        cat = Category.objects.create(title="Test", slug="test")
        product = Product.objects.create(
            category=cat, title="Detail Product", slug="detail-prod",
            price=500, stock=5, status=1
        )
        url = reverse('api-v1:product-detail', kwargs={'pk': product.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Detail Product"