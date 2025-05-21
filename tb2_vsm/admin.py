from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import Step, Process, TonieboxProduction, Location, FactoryCloud, Equipment

from django.urls import path
from django.template.response import TemplateResponse
from .models import Location
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg, Min, Max, Sum, F, FloatField



admin.site.site_header = "TB2 Production Administration"
admin.site.site_title = "TB2 Production Admin Portal"
admin.site.index_title = "TB2 Production Administration"



@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'cycle_time', 
        'amount_of_operators', 
        'output_per_hour', 
        'order', 
        'process_name',
    ]
    list_filter = ['process']
    exclude = ['output_per_hour']

    def process_name(self, obj):
        return obj.process.name if obj.process else '-'
    
    process_name.short_description = 'Process'

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
    list_display = ['id', 'name', 'location', 'active', 'category',]
    list_filter = ['location', 'category']
    filter_horizontal = ('processes',)

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['name', 'production_lines']
    list_filter = ['toniebox_productions']

    def production_lines(self, obj):
        links = []
        for prod in obj.toniebox_productions.all():
            url = reverse('admin:tb2_vsm_tonieboxproduction_change', args=[prod.id])
            name = prod.name or f"Production {prod.id}"
            links.append(f'<a href="{url}">{name}</a>')
        return format_html(", ".join(links))

    production_lines.short_description = "Production Lines"

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        'supplier_name', 'country',
        'production_lines_count',
        'toniebox_1_production_lines_count',
        'toniebox_1_active_count',
        'toniebox_1_inactive_count',
        'toniebox_2_production_lines_count',
        'toniebox_2_active_count',
        'toniebox_2_inactive_count',
        'factory_clouds_counts',
        'is_there_factory_cloud_count',
        'total_operators',
        'active',
    ]
    list_filter = ['country']

    def production_lines_count(self, obj):
        return obj.toniebox_productions.count()
    production_lines_count.short_description = "Production Lines"

    def toniebox_1_production_lines_count(self, obj):
        return obj.toniebox_productions.filter(category=TonieboxProduction.TONIEBOX_1).count()
    toniebox_1_production_lines_count.short_description = "Toniebox 1 Production Lines"

    def toniebox_1_active_count(self, obj):
        return obj.toniebox_productions.filter(category=TonieboxProduction.TONIEBOX_1, active=True).count()
    toniebox_1_active_count.short_description = "Toniebox 1 Active"

    def toniebox_1_inactive_count(self, obj):
        return obj.toniebox_productions.filter(category=TonieboxProduction.TONIEBOX_1, active=False).count()
    toniebox_1_inactive_count.short_description = "Toniebox 1 Inactive"

    def toniebox_2_production_lines_count(self, obj):
        return obj.toniebox_productions.filter(category=TonieboxProduction.TONIEBOX_2).count()
    toniebox_2_production_lines_count.short_description = "Toniebox 2 Production Lines"

    def toniebox_2_active_count(self, obj):
        return obj.toniebox_productions.filter(category=TonieboxProduction.TONIEBOX_2, active=True).count()
    toniebox_2_active_count.short_description = "Toniebox 2 Active"

    def toniebox_2_inactive_count(self, obj):
        return obj.toniebox_productions.filter(category=TonieboxProduction.TONIEBOX_2, active=False).count()
    toniebox_2_inactive_count.short_description = "Toniebox 2 Inactive"


    def factory_clouds_counts(self, obj):
        return obj.factory_clouds.count()
    factory_clouds_counts.short_description = "Factory Clouds"

    def is_there_factory_cloud_count(self, obj):
        return obj.factory_clouds.exists()
    is_there_factory_cloud_count.boolean = True
    is_there_factory_cloud_count.short_description = "Has Factory Cloud"

    def total_operators(self, obj):
        total = 0
        for production in obj.toniebox_productions.all():
            total += production.total_operators()
        return total
    total_operators.short_description = "Total Operators"


@admin.register(FactoryCloud)
class FactoryCloudAdmin(admin.ModelAdmin):
    list_display = ['fc_id', 'name', 'url_link', 'location', 'is_backup', 'linked_production_lines']
    list_filter = ['location', 'is_backup']
    search_fields = ['fc_id', 'name']
    exclude = ['name']

    def url_link(self, obj):
        return format_html(f'<a href="{obj.url}" target="_blank">{obj.url}</a>')
    url_link.short_description = "URL"

    def linked_production_lines(self, obj):
        links = []
        for prod in obj.production_lines.all():
            url = reverse('admin:tb2_vsm_tonieboxproduction_change', args=[prod.id])
            name = prod.name or f"Production {prod.id}"
            links.append(f'<a href="{url}">{name}</a>')
        return format_html(", ".join(links)) if links else "-"
    linked_production_lines.short_description = "Production Lines"


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'serial_number', 'category', 'name', 'location','backup', 'active']
    list_filter = ['location', 'category', 'backup', 'active']
    search_fields = ['serial_number', 'name', 'active']