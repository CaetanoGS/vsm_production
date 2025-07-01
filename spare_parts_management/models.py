from django.db import models
from tb2_vsm.models import Location


class Producer(models.Model):
    name = models.CharField(max_length=255)
    telephone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    ticket_system = models.URLField(blank=True, null=True)

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

    TONIEBOX_1 = "Toniebox 1"
    TONIEBOX_2 = "Toniebox 2"
    TMS = "TMS"
    MTS = " MTS"
    TMES = "TMES"
    OTHER = "Other"

    CATEGORY_CHOICES = [
        (TONIEBOX_1, "Toniebox 1"),
        (TONIEBOX_2, "Toniebox 2"),
        (MTS, "MTS"),
        (TMS, "TMS"),
        (TMES, "TMES"),
        (OTHER, "Other"),
    ]

    name = models.CharField(max_length=255)
    minimum_quantity = models.PositiveIntegerField()
    current_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Price in Euros (€)",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    producer = models.ForeignKey(
        Producer, on_delete=models.SET_NULL, null=True, blank=True
    )
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=TONIEBOX_2,
        null=True,
        blank=True,
    )
    notes = models.TextField(
        blank=True, null=True, help_text="Optional notes of the backup equipment"
    )

    def save(self, *args, **kwargs):
        if self.current_quantity < 1:
            self.status = "Critical"
        elif (
            self.current_quantity < self.minimum_quantity and self.current_quantity >= 1
        ):
            self.status = "Low"
        else:
            self.status = "Stable"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.location.supplier_name})"
