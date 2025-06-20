from django.db import models

from tb2_vsm.models import Location


class ProcessImprovementSuggestion(models.Model):
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="improvement_suggestions",  # Add this line
    )
    suggestion_output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suggestion for {self.location} at {self.created_at}"

