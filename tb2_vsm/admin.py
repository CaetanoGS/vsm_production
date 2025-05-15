from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import Step, Process, TonieboxProduction, Location

from django.urls import path
from django.template.response import TemplateResponse
from .models import Location


admin.site.site_header = "TB2 Production Administration"
admin.site.site_title = "TB2 Production Admin Portal"
admin.site.index_title = "TB2 Production Administration"

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['name', 'cycle_time', 'amount_of_operators', 'output_per_hour', 'order']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('step-tree-view/', self.admin_site.admin_view(self.step_tree_view), name='step-tree-view'),
            path('vsm-lean-view/', self.admin_site.admin_view(self.vsm_lean_view), name='vsm-lean-view'),
        ]
        return custom_urls + urls

    def step_tree_view(self, request):
        locations = Location.objects.select_related('country').prefetch_related(
            'toniebox_productions__processes__steps'
        ).all()

        context = dict(
            self.admin_site.each_context(request),
            locations=locations,
            title='Step Tree View (Hierarchical)',
        )
        return TemplateResponse(request, "admin/step_tree_view.html", context)

    def step_tree_view(self, request):
        locations = Location.objects.prefetch_related(
            'toniebox_productions__processes__steps'
        ).all()

        context = dict(
            self.admin_site.each_context(request),
            locations=locations,
            title='Step Tree View (Hierarchical)',
        )
        return TemplateResponse(request, "admin/step_tree_view.html", context)

    def vsm_lean_view(self, request):
        locations = Location.objects.prefetch_related(
            'toniebox_productions__processes__steps'
        ).all()

        context = dict(
            self.admin_site.each_context(request),
            locations=locations,
            title='Production Structure',
        )
        return TemplateResponse(request, "admin/vsm_lean_view.html", context)



@admin.register(TonieboxProduction)
class TonieboxProductionAdmin(admin.ModelAdmin):
    list_display = ['id', 'location']
    filter_horizontal = ('processes',)  # This should work now, as processes is ManyToMany

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Location)
