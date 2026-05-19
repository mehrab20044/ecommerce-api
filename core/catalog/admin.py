from django.contrib import admin
from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "slug"]
    prepopulated_fields = {
        "slug": ["title"]
    }


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "category",
        "price",
        "stock",
        "is_active",
        "created_date",
    ]
    list_filter = ["category", "is_active", "created_date"]
    search_fields = ["title", "description"]
    prepopulated_fields = {
        "slug": ["title"]
    }
    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "is_main"]

