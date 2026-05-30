from django.contrib import admin
from .models import OrderModel,OrderItemModel


class OrderItemInline(admin.TabularInline):
    model = OrderItemModel
    extra = 0
    readonly_fields = ["product", "product_title","product_price","quantity"]


@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "phone_number",
        "total_price",
        "total_quantity",
        "created_date",    
    ]
    list_filter = ["status","created_date"]
    search_fields = ["user__email","user__username","phone_number"]
    readonly_fields= ["created_date","updated_date"]
    inlines = [OrderItemInline]

@admin.register(OrderItemModel)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=[
        "id",
        "order",
        "product",
        "product_title",
        "product_price",
        "quantity",
        "total_item_price",
    ]