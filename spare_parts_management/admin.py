from django.contrib import admin
from .models import BackupEquipment


class BackupEquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "minimum_quantity",
        "current_quantity",
        "status",
        "location",
        "producer_name",
        "buyer_name",
    ]

    def producer_name(self, obj):
        return obj.producer.name if obj.producer else "-"

    producer_name.admin_order_field = "producer__name"
    producer_name.short_description = "Producer"

    def buyer_name(self, obj):
        return obj.buyer.full_name if obj.buyer else "-"

    buyer_name.admin_order_field = "buyer__full_name"
    buyer_name.short_description = "Buyer"


admin.site.register(BackupEquipment, BackupEquipmentAdmin)
