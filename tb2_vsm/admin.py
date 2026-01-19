import os
import google.generativeai as genai
from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse
from .models import (
    EquipmentSerial,
    Step,
    Process,
    TonieboxProduction,
    Location,
    FactoryCloud,
    Equipment,
)

from django.urls import path
from django.template.response import TemplateResponse
from .models import Location
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Prefetch
from django.contrib.admin import SimpleListFilter
from tb2_vsm.models import Location
from django import forms
from django.shortcuts import redirect, render
from django.contrib import messages

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

admin.site.site_header = "PSM Production Hub"
admin.site.site_title = "PSM Production Hub"
admin.site.index_title = "PSM Production Hub"


class ProductionLocationFilter(SimpleListFilter):
    title = "location"
    parameter_name = "location"

    def lookups(self, request, model_admin):
        from tb2_vsm.models import Location

        return [(loc.id, str(loc)) for loc in Location.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                process__toniebox_productions__location__id=self.value()
            ).distinct()
        return queryset


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "cycle_time",
        "amount_of_operators",
        "output_per_hour",
        "order",
        "process_name",
        "location",
    ]
    list_filter = ["process", ProductionLocationFilter]
    exclude = ["output_per_hour"]

    @admin.display(description="Location")
    def location(self, obj):
        if obj.process:
            productions = obj.process.toniebox_productions.all()
            if productions:
                # Just show the first location if multiple are linked
                location = productions[0].location
                return str(location) if location else "-"
        return "-"

    def process_name(self, obj):
        return obj.process.name if obj.process else "-"

    process_name.short_description = "Process"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "step-tree-view/",
                self.admin_site.admin_view(self.step_tree_view),
                name="step-tree-view",
            ),
            path(
                "vsm-lean-view/",
                self.admin_site.admin_view(self.vsm_lean_view),
                name="vsm-lean-view",
            ),
            path(
                "vsm-lean-tonies-view/",
                self.admin_site.admin_view(self.vsm_lean_view_tonies),
                name="vsm-lean-tonies-view",
            ),
        ]
        return custom_urls + urls

    def build_mermaid_graph(self, location, index):
        def _val(v):
            if callable(v):
                v = v()
            return v or 0

        lines = ["graph TD"]

        active_productions = getattr(
            location,
            "filtered_productions",
            location.toniebox_productions.filter(active=True),
        )

        if not active_productions:
            return ""

        total_ops = sum(_val(p.total_operators) for p in active_productions)
        avg_cts = [_val(p.average_cycle_time) for p in active_productions]
        avg_ct = round(sum(avg_cts) / len(avg_cts), 2) if avg_cts else 0
        min_out = min(
            (_val(p.minimum_output_per_hour) for p in active_productions), default=0
        )

        loc_label = (
            f"🌍 {location.country.name} <br>({location.supplier_name})<br><small>"
            f"Operators: {total_ops}, CT: {avg_ct}s, Min Out/h: {min_out}"
            "</small>"
        )
        lines.append(f'L_{index}["{loc_label}"]')

        for j, prod in enumerate(active_productions, 1):
            prod_ops = _val(prod.total_operators)
            prod_ct = _val(prod.average_cycle_time)
            prod_min = _val(prod.minimum_output_per_hour)
            prod_label = (
                f"📦 {prod.name}<br><small>"
                f"Operators: {prod_ops}, CT: {prod_ct}s, Min Out/h: {prod_min}"
                "</small>"
            )
            lines.append(f'P_{index}_{j}["{prod_label}"]')
            lines.append(f"L_{index} --> P_{index}_{j}")

            for k, proc in enumerate(prod.processes.all().order_by("order"), 1):
                proc_ops = _val(proc.total_operators)
                proc_ct = _val(proc.average_cycle_time)
                proc_min = _val(proc.minimum_output_per_hour)
                proc_label = (
                    f"⚙️ {proc.name}<br><small>"
                    f"Operators: {proc_ops}, CT: {proc_ct}s, Min Out/h: {proc_min}"
                    "</small>"
                )
                lines.append(f'C_{index}_{j}_{k}["{proc_label}"]')
                lines.append(f"P_{index}_{j} --> C_{index}_{j}_{k}")

                for m, step in enumerate(proc.steps.all(), 1):
                    step_ct = _val(step.cycle_time)
                    warning = "⚠️ " if step_ct > prod_ct else ""
                    step_label = (
                        f"{warning}🔧 {step.name}<br><small>"
                        f"CT: {step_ct}s, Ops: {step.amount_of_operators}"
                        "</small>"
                    )
                    lines.append(f'S_{index}_{j}_{k}_{m}["{step_label}"]')
                    lines.append(f"C_{index}_{j}_{k} --> S_{index}_{j}_{k}_{m}")

        return "\n".join(lines)

    def step_tree_view(self, request):
        locations = Location.objects.filter(active=True).prefetch_related(
            Prefetch(
                "toniebox_productions",
                queryset=TonieboxProduction.objects.filter(
                    active=True
                ).prefetch_related("processes__steps"),
                to_attr="filtered_productions",
            )
        )

        context = dict(
            self.admin_site.each_context(request),
            locations=locations,
            title="Step Tree View (Hierarchical)",
        )
        return TemplateResponse(request, "admin/step_tree_view.html", context)

    def vsm_lean_view(self, request):
        toniebox_productions = TonieboxProduction.objects.filter(
            active=True, category__in=["Toniebox 1", "Toniebox 2", "Toniebox 2 G2"]
        ).prefetch_related("processes__steps")

        locations = (
            Location.objects.filter(active=True)
            .prefetch_related(
                Prefetch(
                    "toniebox_productions",
                    queryset=toniebox_productions,
                    to_attr="filtered_productions",
                )
            )
            .distinct()
        )

        mermaid_graphs = []
        for idx, location in enumerate(locations, 1):
            graph = self.build_mermaid_graph(location, idx)
            if graph:
                mermaid_graphs.append((graph, location))

        context = dict(
            self.admin_site.each_context(request),
            locations=locations,
            mermaid_graphs=mermaid_graphs,
            title="Production Structure",
        )
        return TemplateResponse(request, "admin/vsm_lean_view.html", context)

    def vsm_lean_view_tonies(self, request):
        toniebox_productions = (
            TonieboxProduction.objects.filter(active=True)
            .exclude(category__in=["Toniebox 1", "Toniebox 2", "Toniebox 2 G2"])
            .prefetch_related("processes__steps")
        )

        locations = (
            Location.objects.filter(active=True)
            .prefetch_related(
                Prefetch(
                    "toniebox_productions",
                    queryset=toniebox_productions,
                    to_attr="filtered_productions",
                )
            )
            .distinct()
        )

        mermaid_graphs = []
        for idx, location in enumerate(locations, 1):
            graph = self.build_mermaid_graph(location, idx)
            if graph:
                mermaid_graphs.append((graph, location))

        context = dict(
            self.admin_site.each_context(request),
            locations=locations,
            mermaid_graphs=mermaid_graphs,
            title="Production Structure",
        )
        return TemplateResponse(request, "admin/vsm_lean_view_tonies.html", context)


@admin.register(TonieboxProduction)
class TonieboxProductionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "location",
        "active",
        "category",
    ]
    list_filter = ["location", "category"]
    filter_horizontal = ("processes",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "setup-production-tool/",
                self.admin_site.admin_view(self.production_setup_tool_view),
                name="setup_production_tool",
            ),
            path(
                "production-report/<int:location_id>/<str:category>/",
                self.admin_site.admin_view(self.production_report_view),
                name="production_report",
            ),
            path(
                "get-step-suggestion/<int:step_id>/",
                self.admin_site.admin_view(self.get_step_suggestion_view),
                name="get_step_suggestion",
            ),
        ]
        return custom_urls + urls

    def production_setup_tool_view(self, request):
        if request.method == "POST":
            form = ProductionSetupForm(request.POST)
            if form.is_valid():
                category = form.cleaned_data["category"]
                location = form.cleaned_data["location"]
                return redirect(
                    "admin:production_report",
                    location_id=location.id,
                    category=category,
                )
        else:
            form = ProductionSetupForm()

        context = {
            **self.admin_site.each_context(request),
            "title": "Production Setup Tool",
            "form": form,
            "opts": self.model._meta,
        }
        return render(request, "admin/setup_production.html", context)

    def get_step_suggestion_view(self, request, step_id):
        import google.generativeai as genai
        import os
        from django.http import JsonResponse

        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse(
                    {"error": "Configurarion Error: GEMINI_API_KEY not found .env"},
                    status=500,
                )

            step = Step.objects.get(id=step_id)

            if not step.description or not step.description.strip():
                return JsonResponse(
                    {
                        "error": "Step description is required to generate AI suggestions."
                    },
                    status=400,
                )

            genai.configure(api_key=api_key)

            model = genai.GenerativeModel("models/gemini-2.0-flash")

            prompt = (
                f"Evaluate industrial step '{step.name}' which takes {step.cycle_time}s. "
                f"Task description: {step.description}. "
                "Provide a concise, technically specific recommendation in English to reduce cycle time, "
                "based strictly on globally recognized industrial standards (Lean, Kaizen). "
                "Analyze if the time spent is consistent with the described movements. "
                "Focus on measurable actions, ergonomics, or tooling changes. Limit to two sentences."
            )

            response = model.generate_content(prompt)

            if not response.parts:
                return JsonResponse(
                    {"error": "Gemini blocked the response due to safety filters."},
                    status=500,
                )

            return JsonResponse({"suggestion": response.text})

        except Step.DoesNotExist:
            return JsonResponse({"error": "Step not found."}, status=404)
        except Exception as e:
            print(f"DEBUG GEMINI ERROR: {str(e)}")
            return JsonResponse({"error": f"Gemini Error: {str(e)}"}, status=500)

    def production_report_view(self, request, location_id, category):
        location_data = (
            Location.objects.filter(id=location_id)
            .prefetch_related(
                "toniebox_productions",
                "toniebox_productions__processes",
                "toniebox_productions__processes__steps",
            )
            .first()
        )

        if not location_data:
            messages.error(request, "Location not found.")
            return redirect("admin:setup_production_tool")

        filtered_productions = location_data.toniebox_productions.filter(
            category=category, active=True
        )

        context = {
            **self.admin_site.each_context(request),
            "title": f"Production Report: {category} - {location_data.supplier_name}",
            "location": location_data,
            "productions": filtered_productions,
            "category_name": category,
            "opts": self.model._meta,
        }
        return render(request, "admin/production_report.html", context)

    def get_fields(self, request, obj=None):
        """Hide name field when creating, show when editing"""
        fields = super().get_fields(request, obj)
        if obj is None:
            return [f for f in fields if f != "name"]
        return fields

    def save_model(self, request, obj, form, change):
        """Auto-generate name on create"""
        super().save_model(request, obj, form, change)
        if not change and not obj.name:
            obj.name = f"Production {obj.id}"
            obj.save()


class LocationFilter(SimpleListFilter):
    title = "location"
    parameter_name = "location"

    def lookups(self, request, model_admin):
        locations = set()
        for process in model_admin.model.objects.all():
            for prod in process.toniebox_productions.all():
                loc = prod.location
                if loc:
                    locations.add((loc.id, str(loc)))
        return sorted(locations, key=lambda x: x[1])

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                toniebox_productions__location__id=self.value()
            ).distinct()
        return queryset


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ["order", "name", "production_lines", "locations"]
    list_filter = [
        "toniebox_productions",
        LocationFilter,
    ]
    ordering = ["order"]

    def production_lines(self, obj):
        links = []
        for prod in obj.toniebox_productions.all():
            url = reverse("admin:tb2_vsm_tonieboxproduction_change", args=[prod.id])
            name = prod.name or f"Production {prod.id}"
            links.append(f'<a href="{url}">{name}</a>')
        return format_html(", ".join(links))

    production_lines.short_description = "Production Lines"

    def locations(self, obj):
        links = {}
        for prod in obj.toniebox_productions.all():
            location = prod.location
            if location and location.id not in links:
                url = reverse("admin:tb2_vsm_location_change", args=[location.id])
                name = str(location)
                links[location.id] = f'<a href="{url}">{name}</a>'
        return format_html(", ".join(links.values())) or "—"

    locations.short_description = "Locations"


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = [
        "supplier_name",
        "country",
        "production_lines_count",
        "is_there_factory_cloud_count",
        "factory_clouds_counts",
        "total_operators",
        "active",
    ]
    list_filter = ["country"]
    exclude = ["toniebox_production"]

    def production_lines_count(self, obj):
        return obj.toniebox_productions.count()

    production_lines_count.short_description = "Production Lines"

    def factory_clouds_counts(self, obj):
        return obj.factory_clouds.count()

    factory_clouds_counts.short_description = "Factory Clouds"

    def is_there_factory_cloud_count(self, obj):
        return obj.factory_clouds.exists()

    is_there_factory_cloud_count.boolean = True
    is_there_factory_cloud_count.short_description = "Has Factory Cloud"

    def total_operators(self, obj):
        total = 0
        for production in obj.toniebox_productions.filter(active=True):
            total += production.total_operators()
        return total

    total_operators.short_description = "Total Operators (Active Lines Only)"


@admin.register(FactoryCloud)
class FactoryCloudAdmin(admin.ModelAdmin):
    list_display = [
        "fc_id",
        "name",
        "url_link",
        "location",
        "is_backup",
        "linked_production_lines",
    ]
    list_filter = ["location", "is_backup"]
    search_fields = ["fc_id", "name"]
    exclude = ["name"]

    def url_link(self, obj):
        return format_html(f'<a href="{obj.url}" target="_blank">{obj.url}</a>')

    url_link.short_description = "URL"

    def linked_production_lines(self, obj):
        links = []
        for prod in obj.production_lines.all():
            url = reverse("admin:tb2_vsm_tonieboxproduction_change", args=[prod.id])
            name = prod.name or f"Production {prod.id}"
            links.append(f'<a href="{url}">{name}</a>')
        return format_html(", ".join(links)) if links else "-"

    linked_production_lines.short_description = "Production Lines"


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "category",
        "name",
        "location",
        "backup",
        "active",
        "production_type",
        "quantity",
        "serial_numbers_display",
    ]
    list_filter = ["location", "category", "backup", "active", "production_type"]
    search_fields = ["name", "active", "production_type"]
    readonly_fields = [
        "serial_numbers_display",
    ]

    def serial_numbers_display(self, obj):
        serials = obj.serials.all()
        if not serials.exists():
            return "-"
        return ", ".join(s.serial_number for s in serials)

    serial_numbers_display.short_description = "Serial Numbers"


class EquipmentSerialProxy(EquipmentSerial):
    class Meta:
        proxy = True
        verbose_name = "Equipment Serial Number"
        verbose_name_plural = "Equipment Serial Numbers"


@admin.register(EquipmentSerialProxy)
class EquipmentSerialAdmin(admin.ModelAdmin):
    list_display = [
        "serial_number",
        "equipment",
        "equipment_location",
        "is_backup_equipment",
        "notes",
    ]
    search_fields = ("serial_number", "equipment__name")
    list_filter = (
        "equipment__location",
        "equipment__production_type",
        "equipment__category",
    )

    @admin.display(description="Location")
    def equipment_location(self, obj):
        if obj.equipment and obj.equipment.location:
            return str(obj.equipment.location)
        return "—"

    @admin.display(boolean=True, description="Is Backup")
    def is_backup_equipment(self, obj):
        return obj.equipment.backup if obj.equipment else None


class ProductionSetupForm(forms.Form):
    """
    Form to handle category and location selection within the admin.
    """

    category = forms.ChoiceField(
        choices=TonieboxProduction.CATEGORY_CHOICES,
        label="Product Category",
        widget=forms.Select(attrs={"style": "width: 300px;"}),
    )
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(active=True),
        label="Production Location",
        empty_label="--- Select a Location ---",
        widget=forms.Select(attrs={"style": "width: 300px;"}),
    )
