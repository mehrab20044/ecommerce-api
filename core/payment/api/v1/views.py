from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from payment.models import PaymentModel, PaymentStatus
from .serializers import PaymentSerializer
from order.models import OrderStatus


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return PaymentModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="verify")
    def verify(self, request):
        payment_id = request.data.get("payment_id")
        success = request.data.get("success")

        if payment_id is None or success is None:
            return Response(
                {"detail": "payment_id and success are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = PaymentModel.objects.filter(
            id=payment_id,
            user=request.user
        ).select_related("order").first()

        if not payment:
            return Response(
                {"detail": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if payment.status != PaymentStatus.PENDING:
            return Response(
                {"detail": "Payment already processed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if success is True:
            payment.status = PaymentStatus.SUCCESS
            payment.ref_id = "FAKE_REF_123" 
            order = payment.order
            order.status = OrderStatus.PAID
            order.save(update_fields=["status"])

        else:
            payment.status = PaymentStatus.FAILED

        payment.save(update_fields=["status", "ref_id"])

        return Response(
            {
                "payment_id": payment.id,
                "status": payment.status,
            },
            status=status.HTTP_200_OK
        )