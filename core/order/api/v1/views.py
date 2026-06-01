from rest_framework import viewsets, permissions,status
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response


from ...models import OrderModel,OrderItemModel
from cart.models import CartModel

from .serializers import OrderSerializers,CheckoutSerializer

class OrderViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class= OrderSerializers

    def get_queryset(self):
        return(
            OrderModel.objects.filter(user=self.request.user)
            .prefetch_related("items__product")
            .order_by("-created_date")
            )
    @action(detail=False, methods=["post"], url_path="checkout")
    def checkout(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = (
            CartModel.objects
            .filter(user=request.user)
            .prefetch_related("cart_items__product")
            .first()
        )

        if not cart:
            return Response(
                {"detail": "Cart not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = cart.cart_items.all()

        if not cart_items.exists():
            return Response(
                {"detail": "Your cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            order = OrderModel.objects.create(
                user=request.user,
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                phone_number=serializer.validated_data["phone_number"],
                address=serializer.validated_data["address"],
                postal_code=serializer.validated_data.get("postal_code", ""),
            )

            order_items = []
            for cart_item in cart_items:
                product = cart_item.product

                order_items.append(
                    OrderItemModel(
                        order=order,
                        product=product,
                        product_title=product.title,
                        product_price=product.price,
                        quantity=cart_item.quantity,
                    )
                )

            OrderItemModel.objects.bulk_create(order_items)
            cart_items.delete()

        output_serializer = OrderSerializers(
            order,
            context={"request": request}
        )

        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )