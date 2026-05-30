from django.contrib import admin

from .models import PaymentModel


@admin.register(PaymentModel)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "order",
        "amount",
        "status",
        "authority",
        "ref_id",
        "created_date",
    )
    list_filter = ("status", "created_date")
    search_fields = (
        "user__phone_number",
        "user__email",
        "order__id",
        "authority",
        "ref_id",
    )
    readonly_fields = (
        "authority",
        "created_date",
        "updated_date",
    )
    ordering = ("-created_date",)