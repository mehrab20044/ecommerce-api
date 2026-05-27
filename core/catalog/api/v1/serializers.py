from rest_framework import serializers
from ...models import ProductImage, Category,Product
from django.db.models import Avg


class ProductImageserializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'file']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']



        
 
class ProductSerializer(serializers.ModelSerializer):

    images = ProductImageserializer(many=True,read_only=True)
    relative_url = serializers.URLField(source = 'get_absolute_api_url',read_only = True)
    
    
    class Meta:
            model = Product
            fields = [
                'id',
                'title',
                'slug',
                'description',
                'price',
                'stock',
                'status',
                'category',
                'images',
                'relative_url',                
            ]





