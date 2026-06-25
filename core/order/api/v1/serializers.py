from rest_framework import serializers

from order.models import OrderModel, OrderItemModel

class OrderItemSerializers(serializers.ModelSerializer):
    total_item_price = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)

    class Meta:
        model = OrderItemModel
        fields= [
            "id",
            "product",
            "product_title",
            "product_price",
            "quantity",
            "total_item_price",
        ]
        read_only_fields = [
            "id",
            "product",
            "product_title",
            "product_price",
            "quantity",
            "total_item_price",
        ]

class OrderSerializers(serializers.ModelSerializer):
    items= OrderItemSerializers(many=True,read_only=True)
    total_price = serializers.DecimalField(max_digits=10,decimal_places=2,read_only=True)

    class Meta:
        model = OrderModel
        fields=[
            "id",
            "user",
            "status",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "postal_code",
            "items",
            "total_price",
            "total_quantity",
            "created_date",
            "updated_date",
        ]
        read_only_fields = [
            "id",
            "user",
            "status",
            "items",
            "total_price",
            "total_quantity",
            "created_date",
            "updated_date",
        ]

class CheckoutSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=20)
    address = serializers.CharField()
    postal_code = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True
    )

class OrderHistorySerializer(serializers.ModelSerializer):
    item = OrderItemSerializers(many=True, read_only=True)


    class Meta:
        model = OrderModel
        fields =[
            
            "id",
            "status",
            "first_name",
            "last_name",
            "phone_number",
            "address",
            "postal_code",
            "item",
            "total_price",
            "total_quantity",
            "created_date",
            "updated_date",
        ]
        