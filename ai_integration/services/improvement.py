from django.db.models import Max

from ai_integration.models import ProcessImprovementSuggestion
from tb2_vsm.models import Location, Step, TonieboxProduction


def generate_improvement_if_needed(location: Location):
    latest_suggestion = location.improvement_suggestions.first()

    production_lines = TonieboxProduction.objects.filter(location=location).distinct()

    processes = []
    for production in production_lines:
        processes.extend(production.processes.all())

    if not processes:
        return latest_suggestion

    latest_step_update = Step.objects.filter(process__in=processes).aggregate(
        latest=Max("updated_at")
    )["latest"]

    if (
        latest_suggestion
        and latest_step_update
        and latest_step_update <= latest_suggestion.created_at
    ):
        return latest_suggestion

    suggestion_html = generate_analysis_html(location)
    suggestion = ProcessImprovementSuggestion.objects.create(
        location=location, suggestion_output=suggestion_html
    )
    return suggestion


def generate_analysis_html(location):
    html = f"<h2>Improvement Suggestions for {location}</h2>"
    productions = TonieboxProduction.objects.filter(location=location).distinct()
    processed_process_ids = set()

    for production in productions:
        for process in production.processes.all():
            if process.id in processed_process_ids:
                continue
            processed_process_ids.add(process.id)

            html += f"<h3>Process: {process.name}</h3><ul>"
            for step in process.steps.all():
                html += (
                    f"<li><strong>Step:</strong> {step.name}<br>"
                    f"Cycle Time: {step.cycle_time}s<br>"
                    f"Operators: {step.amount_of_operators}<br>"
                    "✅ On target</li>"
                )
            html += "</ul>"
    return html
