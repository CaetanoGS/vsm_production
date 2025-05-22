from django.contrib import admin
from django.utils.html import format_html
from .models import BackupEquipment, Buyer, Producer


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email_link"]

    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)

    email_link.short_description = "Email"


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ["name", "telephone_link", "email_link"]

    def telephone_link(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.telephone, obj.telephone)

    telephone_link.short_description = "Telephone"

    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)

    email_link.short_description = "Email"


@admin.register(BackupEquipment)
class BackupEquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "minimum_quantity",
        "current_quantity",
        "colored_status",
        "location",
        "producer_link",
        "buyer_email_link",
    ]

    def colored_status(self, obj):
        color_map = {
            "Critical": "#f8d7da",  # Light red
            "Low": "#fff3cd",  # Light yellow
            "Stable": "#d4edda",  # Light green
        }
        color = color_map.get(obj.status, "#ffffff")
        return format_html(
            '<span style="background-color: {}; padding: 2px 6px; border-radius: 4px;">{}</span>',
            color,
            obj.status,
        )

    colored_status.short_description = "Status"

    def producer_link(self, obj):
        if obj.producer:
            url = f"/admin/{obj.producer._meta.app_label}/{obj.producer._meta.model_name}/{obj.producer.pk}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.producer.name)
        return "-"

    producer_link.short_description = "Producer"

    def buyer_email_link(self, obj):
        if obj.buyer and obj.buyer.email:
            return format_html(
                '<a href="mailto:{}">{}</a>', obj.buyer.email, obj.buyer.email
            )
        return "-"

    buyer_email_link.short_description = "Buyer Email"
