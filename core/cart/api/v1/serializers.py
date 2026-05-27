from rest_framework import serializers

from ...models import CartItemModel, CartModel
from catalog.api.v1.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_item_price = serializers.DecimalField(
        max_digits=14,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItemModel
        fields = [
            "id",
            "product",
            "quantity",
            "total_item_price",
            "created_date",
            "updated_date",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="cart_items",many=True,read_only=True)
    total_price = serializers.DecimalField(max_digits=14,decimal_places=2,read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartModel
        fields = [
            "id",
            "user",
            "items",
            "total_quantity",
            "total_price",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "user",
            "items",
            "total_quantity",
            "total_price",
            "created_date",
            "updated_date",
        ]

class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)


