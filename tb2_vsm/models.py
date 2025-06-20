from django.db import models
from django_countries.fields import CountryField
from decimal import Decimal


class TonieboxProduction(models.Model):
    """Represents a production batch of Tonieboxes."""

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
        (SOFT_TONIES, "Soft Tonies"),
        (NIGHT_LIGHT, "Night Light"),
        (OTHER, "Other"),
    ]

    name = models.CharField(max_length=100, null=True, blank=True, default=None)
    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="toniebox_productions",
        default=None,
    )

    processes = models.ManyToManyField(
        "Process",
        related_name="toniebox_productions",
        blank=True,
    )
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default=TONIEBOX_2
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name or f"Toniebox Production {self.id}"

    def total_operators(self):
        return sum(process.total_operators() for process in self.processes.all())

    def average_cycle_time(self):
        steps = [
            step for process in self.processes.all() for step in process.steps.all()
        ]
        cycle_times = [step.cycle_time for step in steps if step.cycle_time is not None]
        return round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0

    def minimum_output_per_hour(self):
        steps = [
            step for process in self.processes.all() for step in process.steps.all()
        ]
        output_per_hour = [
            step.output_per_hour for step in steps if step.output_per_hour is not None
        ]
        return min(output_per_hour) if output_per_hour else 0

    class Meta:
        verbose_name = "PSM Production"
        verbose_name_plural = "PSM Productions"


class Process(models.Model):
    """Represents a production process."""

    name = models.CharField(max_length=100, null=True, blank=True, default=None)

    def __str__(self):
        return self.name or "Unnamed Process"

    def total_operators(self):
        """Calculates the total number of operators for all steps in the process."""
        return sum(step.amount_of_operators for step in self.steps.all())

    def average_cycle_time(self):
        """Calculates the average cycle time across all steps in the process."""
        steps = self.steps.all()
        cycle_times = [step.cycle_time for step in steps if step.cycle_time is not None]
        return round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0

    def minimum_output_per_hour(self):
        """Calculates the minimum output per hour across all steps in the process."""
        steps = self.steps.all()
        output_per_hour = [
            step.output_per_hour for step in steps if step.output_per_hour is not None
        ]
        return min(output_per_hour) if output_per_hour else Decimal("0.00")


class Step(models.Model):
    """Represents a step within a process."""

    name = models.CharField(max_length=100, null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=None)
    cycle_time = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, default=None
    )
    amount_of_operators = models.IntegerField(null=True, blank=True, default=0)
    output_per_hour = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, default=None
    )
    order = models.PositiveIntegerField(null=True, blank=True, default=None)
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="steps",
        default=None,
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name or "Unnamed Step"

    def calculate_output_per_hour(self):
        if self.cycle_time is not None:
            return 3600 / self.cycle_time
        return 0

    def save(self, *args, **kwargs):
        self.output_per_hour = self.calculate_output_per_hour()
        super().save(*args, **kwargs)


class Location(models.Model):
    """Represents the location of a Toniebox production."""

    country = CountryField()
    supplier_name = models.CharField(max_length=100)

    toniebox_production = models.ForeignKey(
        TonieboxProduction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="locations",
        default=None,
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.supplier_name} ({self.country})"


class FactoryCloud(models.Model):
    fc_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    url = models.URLField()
    location = models.ForeignKey(
        "Location", on_delete=models.CASCADE, related_name="factory_clouds"
    )
    production_lines = models.ManyToManyField(
        "TonieboxProduction", related_name="factory_clouds", blank=True
    )
    is_backup = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"Factory Cloud {self.fc_id}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Equipment(models.Model):
    LASER_MARKER = "Laser Marker"
    COMPUTER = "Computer"
    SDR = "SDR"
    PRINTER = "Printer"
    USB_HUB = "USB-Hub"
    JIG = "JIG"
    OTHER = "Other"
    TMS = "TMS"
    DISPLAY = "Display"
    NFC_READER = "NFC Reader"
    CAMERA = "Camera"
    SWITCH = "Switch"
    UPS = "UPS"
    FACILITY_CONTROLLER = "Facility Controller"
    SCANNER = "Scanner"
    BUTTON = "Button"
    LIGHT_STRIP = "Light Strip"
    ROUTER = "Router"

    CATEGORY_CHOICES = [
        (LASER_MARKER, "Laser Marker"),
        (COMPUTER, "Computer"),
        (SDR, "SDR"),
        (PRINTER, "Printer"),
        (USB_HUB, "USB-Hub"),
        (JIG, "JIG"),
        (TMS, "TMS"),
        (DISPLAY, "Display"),
        (NFC_READER, "NFC Reader"),
        (CAMERA, "Camera"),
        (SWITCH, "Switch"),
        (UPS, "UPS"),
        (FACILITY_CONTROLLER, "Facility Controller"),
        (SCANNER, "Scanner"),
        (BUTTON, "Button"),
        (LIGHT_STRIP, "Light Strip"),
        (ROUTER, "Router"),
        (OTHER, "Other"),
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

    PRODUCTION_CHOICES = [
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

    production_type = models.CharField(
        max_length=20, choices=PRODUCTION_CHOICES, default=OTHER, null=True, blank=True
    )

    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    name = models.CharField(max_length=255, blank=True, null=True)
    backup = models.BooleanField(default=False)

    location = models.ForeignKey(
        "Location", on_delete=models.CASCADE, related_name="equipments"
    )

    active = models.BooleanField(default=True, editable=False)
    quantity = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.active = not self.backup
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name or self.category} ({self.serial_number or 'No Serial'})"
