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

    TONIEBOX_1 = "Toniebox 1"
    TONIEBOX_2 = "Toniebox 2"
    TONIES = "Tonies"
    BOOK_TONIES = "Book Tonies"
    CLEVER_TONIES = "Clever Tonies"
    DISK = "Disk"
    CONTROLLER = "Controller"
    NIGHT_LIGHT = "Night Light"
    SOFT_TONIES = "Soft Tonies"
    OTHER = "Other"

    CATEGORY_CHOICES = [
        (TONIEBOX_1, "Toniebox 1"),
        (TONIEBOX_2, "Toniebox 2"),
        (TONIES, "Tonies"),
        (BOOK_TONIES, "Book Tonies"),
        (CLEVER_TONIES, "Clever Tonies"),
        (DISK, "Disk"),
        (CONTROLLER, "Controller"),
        (NIGHT_LIGHT, "Night Light"),
        (SOFT_TONIES, "Soft Tonies"),
        (OTHER, "Other"),
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
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=TONIEBOX_2,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        if self.current_quantity <= 1:
            self.status = "Critical"
        elif (
            self.current_quantity < self.minimum_quantity and self.current_quantity > 1
        ):
            self.status = "Low"
        else:
            self.status = "Stable"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.location.supplier_name})"
