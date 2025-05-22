from django.db import models
from tb2_vsm.models import Location


class Producer(models.Model):
    name = models.CharField(max_length=255)
    telephone = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.name


class Buyer(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.full_name


class BackupEquipment(models.Model):
    STATUS_CHOICES = [
        ("Critical", "Critical"),
        ("Low", "Low"),
        ("Stable", "Stable"),
    ]

    name = models.CharField(max_length=255)
    minimum_quantity = models.PositiveIntegerField()
    current_quantity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    producer = models.ForeignKey(
        Producer, on_delete=models.SET_NULL, null=True, blank=True
    )
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)

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
