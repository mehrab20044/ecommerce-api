from django.db import models
from django.core.validators import MaxValueValidator,MinValueValidator
from catalog.models import Product
from django.conf import settings

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="review")
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="review")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment = models.TextField()
    is_active = models.BooleanField(default=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=["-created_date"]
        constraints=[
            models.UniqueConstraint(
                fields=["user","product"],
                name= "unique_user_product_review"
            )
        ]

        def __str__(self):
            return f"Review by {self.user} for {self.product}"