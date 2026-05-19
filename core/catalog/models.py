from django.db import models
from django.urls import reverse

class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug= models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10,decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name='products')
    is_active= models.BooleanField(default=True)

    created_date= models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_date"]


    def __str__(self):
        return self.title
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product,related_name="images",on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products")
    is_main = models.BooleanField(default=False)

    created_date= models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["-is_main", "created_date"]



    def get_absolute_api_url(self):
        return reverse('todo:api-v1:todo-detail', kwargs={'pk':self.pk})


    def __str__(self):
        return f"Image for {self.product.title}"

    
