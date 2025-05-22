from django.db import models
from tb2_vsm.models import Location


class BackupEquipment(models.Model):
    STATUS_CHOICES = [
        ("Critical", "Critical"),
        ("Low", "Low"),
        ("Stable", "Stable"),
    ]

    name = models.CharField(max_length=255)
    minimum_quantity = models.PositiveIntegerField()
    current_quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.current_quantity == 0:
            self.status = "Critical"
        elif self.current_quantity < self.minimum_quantity:
            self.status = "Low"
        else:
            self.status = "Stable"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.location.supplier_name})"
