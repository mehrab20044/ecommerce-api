import pytest
from django.urls import reverse
from rest_framework import status
from catalog.models import Category, Product, ProductStatusType
from cart.models import CartModel, CartItemModel

pytestmark = pytest.mark.django_db

class TestCartAPI:

    def test_get_cart_creates_if_not_exists(self, authenticated_client):
        client, user = authenticated_client
        url = reverse('cart-list')   # بدون cart:
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert "total_price" in response.data
        assert "total_quantity" in response.data
        assert response.data['total_quantity'] == 0

    def test_add_item_to_cart(self, authenticated_client):
        client, user = authenticated_client
        cat = Category.objects.create(title="Test", slug="test")
        product = Product.objects.create(
            category=cat,
            title="Test Product",
            slug="test-product",
            price=50000,
            stock=10,
            status=ProductStatusType.publish.value
        )

        url = reverse('cart-items-list')
        data = {"product_id": product.id, "quantity": 3}
        response = client.post(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_quantity'] == 3
        assert len(response.data.get('items', [])) == 1

    def test_update_cart_item_quantity(self, authenticated_client):
        client, user = authenticated_client
        cat = Category.objects.create(title="Test", slug="test")
        product = Product.objects.create(
            category=cat, title="Test", slug="test", price=1000, 
            stock=10, status=ProductStatusType.publish.value
        )
        
        cart = CartModel.objects.create(user=user)
        item = CartItemModel.objects.create(cart=cart, product=product, quantity=1)

        url = reverse('cart-items-detail', kwargs={'pk': item.pk})
        data = {"quantity": 5}
        response = client.patch(url, data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_quantity'] == 5

    def test_delete_cart_item(self, authenticated_client):
        client, user = authenticated_client
        cat = Category.objects.create(title="Test", slug="test")
        product = Product.objects.create(category=cat, title="Test", slug="test", price=1000, stock=10, status=ProductStatusType.publish.value)
        
        cart = CartModel.objects.create(user=user)
        item = CartItemModel.objects.create(cart=cart, product=product, quantity=2)

        url = reverse('cart-items-detail', kwargs={'pk': item.pk})
        response = client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert not CartItemModel.objects.filter(pk=item.pk).exists()

    def test_clear_cart(self, authenticated_client):
        client, user = authenticated_client
        cat = Category.objects.create(title="Test", slug="test")
        product = Product.objects.create(category=cat, title="Test", slug="test", price=1000, stock=10, status=ProductStatusType.publish.value)
        
        cart = CartModel.objects.create(user=user)
        CartItemModel.objects.create(cart=cart, product=product, quantity=4)

        url = reverse('cart-clear')   # action clear
        response = client.delete(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_quantity'] == 0