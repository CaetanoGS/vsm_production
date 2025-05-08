from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import Step, Process, TonieboxProduction, Location

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['name', 'cycle_time', 'amount_of_operators', 'output_per_hour']

    def get_urls(self):
        # Get default URLs
        urls = super().get_urls()

        # Add custom URL for the step tree view
        custom_urls = [
            path('step-tree-view/', self.admin_site.admin_view(self.step_tree_view), name='step-tree-view'),
        ]

        return custom_urls + urls

    def step_tree_view(self, request):
        # Get all locations and prefetch related production, process, and steps
        locations = Location.objects.prefetch_related(
            'toniebox_productions__processes__steps'
        )

        # Collect all steps from locations and their nested objects
        steps = []
        for location in locations:
            for production in location.toniebox_productions.all():
                for process in production.processes.all():
                    steps.extend(process.steps.all())

        # Calculate the average cycle time for all steps
        cycle_times = [step.cycle_time for step in steps if step.cycle_time is not None]
        average_cycle_time = sum(cycle_times) / len(cycle_times) if cycle_times else 0

        context = {
            'locations': locations,
            'average_cycle_time': average_cycle_time,
        }
        return TemplateResponse(request, 'admin/step_tree_view.html', context)


@admin.register(TonieboxProduction)
class TonieboxProductionAdmin(admin.ModelAdmin):
    list_display = ['id', 'location']
    filter_horizontal = ('processes',)  # This should work now, as processes is ManyToMany

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Location)
