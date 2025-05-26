from django.contrib import admin, messages
from .models import Maintenance
from datetime import date, timedelta
from django.utils.html import format_html


@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = (
        "equipment",
        "last_maintenance_day",
        "next_maintenance_day",
        "colored_status",
        "next_maintenance_in_days_display",
    )

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
        upcoming_maintenances = Maintenance.objects.filter(
            next_maintenance_day__lte=date.today() + timedelta(days=7),
            next_maintenance_day__gte=date.today(),
        )
        if upcoming_maintenances.exists():
            equipment_list = ", ".join(
                f"{m.equipment.name} (Next: {m.next_maintenance_day})"
                for m in upcoming_maintenances
            )
            messages.warning(
                request,
                f"Upcoming Maintenance: {equipment_list}"
            )
        return super().changelist_view(request, extra_context=extra_context)
