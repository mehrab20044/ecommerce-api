from django.db import models
from django.conf import settings
from decimal import Decimal

class CartModel(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    
    @property
    def total_price(self):
        return sum(
            (item.total_item_price for item in self.cart_items.all()),
            Decimal("0.00")
        )

    @property
    def total_quantity(self):
        return sum(
            item.quantity for item in self.cart_items.all()
        )

    def __str__(self):
        return f"Cart of {self.user.email}"

class CartItemModel(models.Model):
    cart = models.ForeignKey(CartModel, on_delete=models.CASCADE, related_name="cart_items") 
    product = models.ForeignKey('catalog.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1) # مقدار پیش‌فرض ۱ منطقی‌تر است
    
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["product", "cart"]

    @property
    def total_item_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.title} - {self.quantity}"
    
        