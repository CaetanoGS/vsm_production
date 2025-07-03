from django.db import models

from tb2_vsm.models import Equipment
from datetime import date


class Maintenance(models.Model):
    STATUS_CHOICES = [
        ("expired", "Expired"),
        ("on_track", "On Track"),
    ]

    equipment = models.OneToOneField(Equipment, on_delete=models.CASCADE)
    last_maintenance_day = models.DateField(blank=True, null=True)
    next_maintenance_day = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        editable=False,
    )

    def __str__(self):
        return f"{self.equipment.name} - {self.status}"

    def next_maintenance_in_days(self):
        if self.next_maintenance_day:
            return (self.next_maintenance_day - date.today()).days
        return None

    def is_expired(self):
        if self.next_maintenance_day:
            return self.next_maintenance_day < date.today()
        return False

    def save(self, *args, **kwargs):
        if self.is_expired():
            self.status = "expired"
        else:
            self.status = "on_track"
        super().save(*args, **kwargs)
