from django.contrib import admin, messages
from .models import Maintenance
from datetime import date, timedelta
from django.utils.html import format_html
from django.urls import reverse


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = (
        "equipment",
        "equipment_id_link",
        "equipment_location",
        "last_maintenance_day",
        "next_maintenance_day",
        "colored_status",
        "next_maintenance_in_days_display",
    )

    def equipment_id_link(self, obj):
        url = reverse("admin:tb2_vsm_equipment_change", args=[obj.equipment.id])
        return format_html('<a href="{}">{}</a>', url, obj.equipment.id)

    equipment_id_link.short_description = "Equipment ID"
    equipment_id_link.admin_order_field = "equipment__id"

    def equipment_location(self, obj):
        return getattr(obj.equipment, "location", None)

    equipment_location.short_description = "Equipment Location"
    equipment_location.admin_order_field = "equipment__location"

    def next_maintenance_in_days_display(self, obj):
        return obj.next_maintenance_in_days()

    next_maintenance_in_days_display.short_description = "Next Maintenance In Days"

    def colored_status(self, obj):
        color = "#ffcccc" if obj.is_expired() else "#ccffcc"
        label = "Expired" if obj.is_expired() else "On Track"
        return format_html(
            '<div style="background-color:{}; border-radius:5px; padding:2px 8px; display:inline-block;">{}</div>',
            color,
            label,
        )

    colored_status.short_description = "Status"

    def changelist_view(self, request, extra_context=None):
        today = date.today()
        upcoming_maintenances = Maintenance.objects.filter(
            next_maintenance_day__lte=today + timedelta(days=7),
            next_maintenance_day__gte=today,
        )
        expired_maintenances = Maintenance.objects.filter(
            next_maintenance_day__lt=today
        )

        maintenance_msgs = []

        if expired_maintenances.exists():
            expired_list = ", ".join(
                f"{m.equipment.name} (Expired: {m.next_maintenance_day})"
                for m in expired_maintenances
            )
            maintenance_msgs.append(f"Expired Maintenance: {expired_list}")

        if upcoming_maintenances.exists():
            upcoming_list = ", ".join(
                f"{m.equipment.name} (Next: {m.next_maintenance_day})"
                for m in upcoming_maintenances
            )
            maintenance_msgs.append(f"Upcoming Maintenance: {upcoming_list}")

        if maintenance_msgs:
            messages.warning(request, " | ".join(maintenance_msgs))

        return super().changelist_view(request, extra_context=extra_context)
