from django.contrib import admin
from django.utils.html import format_html
from .models import BackupEquipment, Buyer, Producer
from decimal import Decimal


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email_link"]

    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)

    email_link.short_description = "Email"


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ["name", "telephone_link", "email_link", "ticket_system_link"]

    def telephone_link(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.telephone, obj.telephone)

    telephone_link.short_description = "Telephone"

    def email_link(self, obj):
        return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)

    email_link.short_description = "Email"

    def ticket_system_link(self, obj):
        if obj.ticket_system:
            return format_html(
                '<a href="{0}" target="_blank">{0}</a>', obj.ticket_system
            )
        return "-"

    ticket_system_link.short_description = "Ticket System"


@admin.register(BackupEquipment)
class BackupEquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "minimum_quantity",
        "current_quantity",
        "colored_status",
        "price",
        "investment_required_display",
        "location",
        "producer_link",
        "buyer_email_link",
        "category",
        "notes"
    ]

    list_filter = ["status", "location", "category"]
    readonly_fields = ["status"]

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

    def investment_required_display(self, obj):
        return self._investment_required(obj)

    investment_required_display.short_description = "Investment Required (€)"

    def _investment_required(self, obj):
        if obj.price is not None and obj.current_quantity < obj.minimum_quantity:
            return (obj.minimum_quantity - obj.current_quantity) * obj.price
        return Decimal("0.00")

    def changelist_view(self, request, extra_context=None):
        queryset = self.get_queryset(request)
        total_investment = sum(self._investment_required(obj) for obj in queryset)

        from django.contrib import messages

        messages.info(
            request,
            f"💶 Total Investment Required for Visible Items: {total_investment:.2f} €",
        )

        return super().changelist_view(request, extra_context=extra_context)

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
