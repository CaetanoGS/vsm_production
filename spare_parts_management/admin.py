from django.contrib import admin
from .models import BackupEquipment, Buyer, Producer


class BackupEquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "minimum_quantity",
        "current_quantity",
        "status",
        "location",
        "producer_name",
        "buyer_email",
    ]

    def producer_name(self, obj):
        return obj.producer.name if obj.producer else "-"

    producer_name.admin_order_field = "producer__name"
    producer_name.short_description = "Producer"

    def buyer_email(self, obj):
        return obj.buyer.email if obj.buyer else "-"

    buyer_email.admin_order_field = "buyer__email"
    buyer_email.short_description = "Buyer Email"


admin.site.register(BackupEquipment, BackupEquipmentAdmin)
admin.site.register(Buyer)
admin.site.register(Producer)