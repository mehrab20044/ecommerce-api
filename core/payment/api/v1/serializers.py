from rest_framework import serializers
from payment.models import PaymentModel
from order.models import OrderModel, OrderStatus


class PaymentSerializers(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PaymentModel
        fields = [
            "id",
            "user",
            "order",
            "order_id",
            "amount",
            "status",
            "authority",
            "ref_id",
            "created_date",
            "updated_date",
        ]

        read_only_fields = [
            "id",
            "user",
            "order",
            "amount",
            "status",
            "authority",
            "ref_id",
            "created_date",
            "updated_date",
        ]

    def validate_order_id(self, value):
        request = self.context["request"]

        try:
            order = OrderModel.objects.get(id=value, user=request.user)
        except OrderModel.DoesNotExist:
            raise serializers.ValidationError("Order not found")

        if order.status != OrderStatus.PENDING:
            raise serializers.ValidationError("Only pending orders can be paid")

        if order.total_price <= 0:
            raise serializers.ValidationError("Invalid order amount")

        self.context["order"] = order
        return value

    def create(self, validated_data):
        request = self.context["request"]
        order = self.context["order"]

        payment = PaymentModel.objects.create(
            user=request.user,
            order=order,
            amount=order.total_price,
            status=PaymentStatus.PENDING
        )

        return payment