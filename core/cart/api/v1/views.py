from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import mixins

from catalog.models import Product, ProductStatusType
from ...models import CartModel, CartItemModel
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
)


class CartViewSet(mixins.ListModelMixin,viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            CartModel.objects
            .filter(user=self.request.user)
            .prefetch_related(
                "cart_items",
                "cart_items__product",
                "cart_items__product__images",
            )
    )

    def list(self, request, *args, **kwargs):
        cart, created = CartModel.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        cart, created = CartModel.objects.get_or_create(user=request.user)
        cart.cart_items.all().delete()

        serializer = self.get_serializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return (
            CartItemModel.objects
            .filter(cart__user=self.request.user)
            .select_related("product", "cart")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return AddCartItemSerializer

        if self.action in ["update", "partial_update"]:
            return UpdateCartItemSerializer

        return CartItemSerializer

    def get_cart(self):
        cart, created = CartModel.objects.get_or_create(user=self.request.user)
        return cart

    def list(self, request, *args, **kwargs):
        cart = self.get_cart()
        cart_serializer = CartSerializer(
            cart,
            context=self.get_serializer_context()
        )
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]

        try:
            product = Product.objects.get(
                id=product_id,
                status=ProductStatusType.publish.value
            )
        except Product.DoesNotExist:
            raise ValidationError({
                "product_id": "Product not found or not published."
            })

        cart = self.get_cart()

        cart_item, created = CartItemModel.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        cart_serializer = CartSerializer(
            cart,
            context=self.get_serializer_context()
        )
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data["quantity"]

        if quantity == 0:
            instance.delete()
        else:
            instance.quantity = quantity
            instance.save()

        cart = self.get_cart()
        cart_serializer = CartSerializer(
            cart,
            context=self.get_serializer_context()
        )
        return Response(cart_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cart = instance.cart

        instance.delete()

        cart_serializer = CartSerializer(
            cart,
            context=self.get_serializer_context()
        )
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
