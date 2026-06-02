from django.db import models
from django.conf import settings
import uuid

from order.models import OrderModel
from common.models import TimeStampMixin


class PaymentStatus(models.TextChoices):
    PENDING = "pending","Pending"
    SUCCESS = "success","Success"
    FAILED = "failed", "Failed"

class PaymentModel(TimeStampMixin):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="payments")
    order = models.OneToOneField(OrderModel,on_delete=models.CASCADE,related_name="payments")
    amount = models.DecimalField(max_digits=14,decimal_places=2)
    status=models.CharField(max_length=20,choices=PaymentStatus.choices,default=PaymentStatus.PENDING)
    authority = models.CharField(max_length=255, blank=True, null=True)
    ref_id = models.CharField(max_length=30,blank=True,null=True)

    class Meta:
        ordering = ["-created_date"]


    def __str__(self):
        return f"Payment #{self.id} - {self.status}"
