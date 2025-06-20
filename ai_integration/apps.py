import openai
from django.apps import AppConfig


class AiIntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ai_integration"
    verbose_name = "WIP - ChatGPT Integration"

def generate_suggestions_for_step(step):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[...],
    )