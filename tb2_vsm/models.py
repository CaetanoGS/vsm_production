from django.db import models
from django_countries.fields import CountryField

class TonieboxProduction(models.Model):
    """Represents a production batch of Tonieboxes."""
    
    # ForeignKey to Location model (optional)
    location = models.ForeignKey(
        'Location',  # The model being referenced
        on_delete=models.SET_NULL,  # What happens when the related Location is deleted
        null=True,  # Allow this field to be null
        blank=True,  # Allow this field to be empty in forms
        related_name='toniebox_productions',  # How you access the related TonieboxProductions from the Location model
        default=None  # Default value when no location is assigned
    )
    
    # Many-to-Many relationship with Process to allow multiple processes for a TonieboxProduction
    processes = models.ManyToManyField(
        'Process',  # The model being referenced
        related_name='toniebox_productions',  # How you access the related TonieboxProductions from Process
        blank=True,  # Allows this relationship to be optional
    )

    def __str__(self):
        return f"Toniebox Production {self.id}"

    def total_operators(self):
        """Calculates the total number of operators for all processes in this production."""
        return sum(process.total_operators() for process in self.processes.all())

    def average_cycle_time(self):
        """Calculates the average cycle time across all steps in the production."""
        steps = [step for process in self.processes.all() for step in process.steps.all()]
        cycle_times = [step.cycle_time for step in steps if step.cycle_time is not None]
        return round(sum(cycle_times) / len(cycle_times), 2) if cycle_times else 0

    def minimum_output_per_hour(self):
        """Calculates the minimum output per hour across all steps in the production."""
        steps = [step for process in self.processes.all() for step in process.steps.all()]
        output_per_hour = [step.output_per_hour for step in steps if step.output_per_hour is not None]
        return min(output_per_hour) if output_per_hour else 0


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
        output_per_hour = [step.output_per_hour for step in steps if step.output_per_hour is not None]
        return min(output_per_hour) if output_per_hour else 0


class Step(models.Model):
    """Represents a step within a process."""
    name = models.CharField(max_length=100, null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True, default=None)
    cycle_time = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=None)
    amount_of_operators = models.IntegerField(null=True, blank=True, default=None)
    output_per_hour = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, default=None)

    # Each step belongs to a process
    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='steps',  # Reverse relationship to access steps from Process
        default=None  # Default value when no process is assigned
    )

    def __str__(self):
        return self.name or "Unnamed Step"
    
    def calculate_output_per_hour(self):
        """Calculates the output per hour based on cycle time (if cycle time is provided)."""
        if self.cycle_time is not None:
            return 3600 / self.cycle_time  # Output per hour based on cycle time in seconds
        return 0  # Return 0 if no cycle time is provided

    def save(self, *args, **kwargs):
        """Override the save method to automatically set output_per_hour based on cycle_time."""
        self.output_per_hour = self.calculate_output_per_hour()
        super().save(*args, **kwargs)


class Location(models.Model):
    """Represents the location of a Toniebox production."""
    country = CountryField()  # Use django_countries for country field
    supplier_name = models.CharField(max_length=100)
    
    # Location is tied to a specific Toniebox production (optional)
    toniebox_production = models.ForeignKey(
        TonieboxProduction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locations',  # Reverse relationship to access locations from TonieboxProduction
        default=None  # Default value when no TonieboxProduction is assigned
    )

    def __str__(self):
        return f"{self.supplier_name} ({self.country})"
