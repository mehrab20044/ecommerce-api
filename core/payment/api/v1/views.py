from rest_framework import viewsets, permissions
from .serializers import PaymentSerializers
from payment.models import PaymentModel
from rest_framework.decorators import action
from rest_framework.response import Response

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializers
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return PaymentModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=["post"])
    def verify(self, request):
        payment_id = request.data.get("payment_id")
        success = request.data.get("success")

        payment = PaymentModel.objects.filter(id=payment_id, user=request.user).first()

        if not payment:
            return Response({"error": "Payment not found"}, status=404)

        if payment.status != "pending":
            return Response({"error": "Already processed"}, status=400)

        if success:
            payment.status = "success"
            payment.ref_id = "FAKE_REF_123"

            payment.order.status = "paid"
            payment.order.save()
        else:
            payment.status = "failed"

        payment.save()

        return Response({"status": payment.status})