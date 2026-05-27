from django.db import models
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
from django.core.validators import MinValueValidator,MaxValueValidator
 


class ProductStatusType(models.IntegerChoices):
    publish = 1 ,("نمایش")
    draft = 2 ,("عدم نمایش")

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return self.title

class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name='products')
    title = models.CharField(max_length=255)
    slug= models.SlugField(unique=True)
    description = models.TextField()
    

    stock = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=ProductStatusType.choices,default=ProductStatusType.draft.value)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    discount_percent = models.IntegerField(default=0,validators = [MinValueValidator(0),MaxValueValidator(100)])

    avg_rate = models.FloatField(default=0.0)


    created_date= models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]


    def __str__(self):
        return self.title
    
    @property
    def get_price(self):        
        discount_amount = self.price * Decimal(self.discount_percent / 100)
        discounted_amount = self.price - discount_amount
        return round(discounted_amount)
    
    def is_discounted(self):
        return self.discount_percent != 0
    
    def is_published(self):
        return self.status == ProductStatusType.publish.value
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product,related_name="images",on_delete=models.CASCADE)
    file = models.ImageField(upload_to="products")
    

    created_date= models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["created_date"]



    def get_absolute_api_url(self):
        return reverse('todo:api-v1:todo-detail', kwargs={'pk':self.pk})


    def __str__(self):
        return f"Image for {self.product.title}"
    


class WishlistProductModel(models.Model):
    user = models.ForeignKey("accounts.User",on_delete=models.PROTECT)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.product.title
    
