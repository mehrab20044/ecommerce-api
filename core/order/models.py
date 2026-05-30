from django.db import models
from decimal import Decimal
from django.conf import settings

from catalog.models import Product


class OrderStatus(models.TextChoices):
    pending = "pending", "Pending"
    paid = "paid", "Paid"
    processing = "processing", "Processing"
    shipped = "shipped", "Shipped"
    delivered = "delivered", "Delivered"
    canceled = "canceled", "Canceled"

class OrderModel(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="orders")
    status= models.CharField(max_length=20,choices=OrderStatus.choices,default=OrderStatus.pending)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number= models.CharField(max_length=20)
    address = models.TextField()
    postal_code = models.CharField(max_length=20,blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=["-created_date"]

    @property
    def total_price(self):
        return sum(
            item.total_item_price for item in self.item.all()
        ) or Decimal("0.00")
    
    @property
    def total_quantity(self):
        return sum(
            item.quantity for item in self.item.all()
        )
    
    def __str__(self):
        return f"order #{self.id} - {self.user} - {self.status}"
    
class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product,on_delete=models.PROTECT,related_name="order_items")
    
    product_title = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10,decimal_places=2)
    quantity =models.PositiveIntegerField(default=1)

    created_date = models.DateTimeField(auto_now_add=True)

    @property
    def total_item_price(self):
        return self.product_price * self.quantity
    
    def __str__(self):
        return f"{self.product_title} x {self.quantity}"
    

