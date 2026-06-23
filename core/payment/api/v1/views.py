from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
import requests
import json

from payment.models import PaymentModel, PaymentStatus
from .serializers import PaymentSerializer
from order.models import OrderModel, OrderStatus


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return PaymentModel.objects.filter(user=self.request.user)

    def get_permissions(self):
        if self.action == "verify":
            return [permissions.AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        order_id = request.data.get("order_id") or request.data.get("order")
        
        if not order_id:
            return Response({"error": "ارسال شناسه سفارش (order_id یا order) الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        order = OrderModel.objects.filter(id=order_id, user=request.user).first()
        
        if not order:
            return Response({"error": "سفارشی با این شناسه یافت نشد یا متعلق به حساب کاربری شما نیست."}, status=status.HTTP_404_NOT_FOUND)

        payment, created = PaymentModel.objects.get_or_create(
            order=order,
            defaults={
                'user': request.user,
                'amount': order.total_price,
                'status': PaymentStatus.PENDING
            }
        )

        if not created:
            payment.status = PaymentStatus.PENDING
            payment.amount = order.total_price
            payment.save(update_fields=["status", "amount"])

        amount = int(payment.amount)

        req_data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount,
            "callback_url": settings.ZARINPAL_CALLBACK_URL,
            "description": f"Payment for order {order.id} by {request.user.phone_number}",
        }
        req_header = {"accept": "application/json", "content-type": "application/json"}
        
        try:
            req = requests.post(url=settings.ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
            response_data = req.json()
            
            if not response_data.get('errors'):
                authority = response_data['data']['authority']
                
                payment.authority = authority
                payment.save(update_fields=["authority"])
                
                payment_url = settings.ZP_API_STARTPAY.format(authority=authority)
                
                return Response(
                    {
                        "payment_id": payment.id,
                        "status": payment.status,
                        "payment_url": payment_url
                    },
                    status=status.HTTP_200_OK
                )
            else:
                payment.status = PaymentStatus.FAILED
                payment.save(update_fields=["status"])
                return Response({"error": response_data['errors']}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.save(update_fields=["status"])
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=["get"], url_path="verify")
    def verify(self, request):
        authority = request.GET.get("Authority")
        payment_status = request.GET.get("Status")

        if not authority or not payment_status:
            return Response(
                {"detail": "Authority and Status query parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = PaymentModel.objects.filter(
            authority=authority,
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

        if payment_status == 'OK':
            amount = int(payment.amount)

            req_data = {
                "merchant_id": settings.ZARINPAL_MERCHANT_ID,
                "amount": amount,
                "authority": authority
            }
            req_header = {"accept": "application/json", "content-type": "application/json"}

            try:
                req = requests.post(url=settings.ZP_API_VERIFICATION, json=req_data, headers=req_header, timeout=10)
                response_data = req.json()
                zarinpal_data = response_data.get("data") or {}
                zarinpal_errors = response_data.get("errors") or response_data.get("error")

                if not zarinpal_errors and zarinpal_data:
                    t_code = zarinpal_data.get('code')

                    if t_code == 100:
                        payment.status = PaymentStatus.SUCCESS
                        payment.ref_id = str(zarinpal_data['ref_id'])
                        payment.save(update_fields=["status", "ref_id"])

                        order = payment.order
                        order.status = OrderStatus.paid
                        order.save(update_fields=["status"])

                        return Response(
                            {
                                "message": "Payment successful",
                                "payment_id": payment.id,
                                "ref_id": payment.ref_id,
                                "status": payment.status
                            },
                            status=status.HTTP_200_OK
                        )
                    elif t_code == 101:
                        return Response({"detail": "Transaction already verified"}, status=status.HTTP_200_OK)
                    else:
                        payment.status = PaymentStatus.FAILED
                        payment.save(update_fields=["status"])
                        return Response({"detail": "Transaction failed"}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    payment.status = PaymentStatus.FAILED
                    payment.save(update_fields=["status"])
                    return Response({"error": zarinpal_errors or response_data}, status=status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            payment.status = PaymentStatus.FAILED
            payment.save(update_fields=["status"])
            return Response(
                {
                    "message": "Payment canceled by user",
                    "payment_id": payment.id,
                    "status": payment.status
                },
                status=status.HTTP_400_BAD_REQUEST
            )