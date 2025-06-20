from django.contrib import admin
from django.utils.safestring import mark_safe

from ai_integration.services.improvement import generate_improvement_if_needed
from tb2_vsm.models import Location
from .models import ProcessImprovementSuggestion


@admin.register(ProcessImprovementSuggestion)
class ProcessImprovementSuggestionAdmin(admin.ModelAdmin):
    list_display = ("location", "created_at")
    readonly_fields = ("location", "created_at", "render_suggestion")
    exclude = ("suggestion_output",)

    def render_suggestion(self, obj):
        return mark_safe(obj.suggestion_output)  # HTML or Markdown-rendered

    render_suggestion.short_description = "Suggestion Result"

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        """
        On listing view, update suggestions for all locations if needed
        """
        for location in Location.objects.all():
            generate_improvement_if_needed(location)

        return super().changelist_view(request, extra_context=extra_context)
