from django.db import models

from tb2_vsm.models import Equipment
from datetime import date, timedelta


class Maintenance(models.Model):
    STATUS_CHOICES = [
        ("expired", "Expired"),
        ("on_track", "On Track"),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    last_maintenance_day = models.DateField(blank=True, null=True)
    next_maintenance_day = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.equipment.name} - {self.status}"

    def next_maintenance_in_days(self):
        return (self.next_maintenance_day - self.last_maintenance_day).days

    def is_expired(self):
        return self.next_maintenance_day < date.today()
