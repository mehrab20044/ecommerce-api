from rest_framework import serializers
from django.db import transaction

from payment.models import PaymentModel, PaymentStatus
from order.models import OrderModel, OrderStatus


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PaymentModel
        fields = ["id", "order_id"]

    def validate_order_id(self, value):
        user = self.context["request"].user

        try:
            order = OrderModel.objects.get(id=value, user=user)
        except OrderModel.DoesNotExist:
            raise serializers.ValidationError("Order not found")

        if order.status != OrderStatus.pending:
            raise serializers.ValidationError("Order cannot be paid")

        if order.total_price <= 0:
            raise serializers.ValidationError("Invalid amount")

        if PaymentModel.objects.filter(
            order=order,
            status=PaymentStatus.PENDING
        ).exists():
            raise serializers.ValidationError(
                "Pending payment already exists"
            )

        return value

    def create(self, validated_data):
        user = self.context["request"].user
        order = OrderModel.objects.get(
            id=validated_data["order_id"],
            user=user
        )

        with transaction.atomic():
            payment = PaymentModel.objects.create(
                user=user,
                order=order,
                amount=order.total_price
            )

        return payment
