from django.contrib import admin, messages
from .models import BackupEquipment


@admin.register(BackupEquipment)
class BackupEquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "location",
        "minimum_quantity",
        "current_quantity",
        "status",
    )
    readonly_fields = ("status",)
    list_filter = ("location", "status")

    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and obj.status == "Critical":
            messages.warning(request, f"Please buy the {obj.name}")
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )
