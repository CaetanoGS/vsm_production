from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import Maintenance
from tb2_vsm.models import Location, Equipment


class MaintenanceModelTest(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            country="DE",  # Germany ISO code
            supplier_name="Test Supplier"
        )
        self.equipment = Equipment.objects.create(
            name="Test Equipment",
            category=Equipment.OTHER,
            location=self.location,
            quantity=1,
            serial_number="SN12345",
            production_type=Equipment.OTHER,
        )
        self.today = timezone.now().date()
        self.last_maintenance = self.today - timedelta(days=30)
        self.next_maintenance = self.today + timedelta(days=30)

    def test_maintenance_creation(self):
        maintenance = Maintenance.objects.create(
            equipment=self.equipment,
            last_maintenance_day=self.last_maintenance,
            next_maintenance_day=self.next_maintenance,
            status="on_track",
        )
        self.assertEqual(maintenance.equipment.name, "Test Equipment")
        self.assertEqual(maintenance.status, "on_track")

    def test_next_maintenance_in_days(self):
        maintenance = Maintenance.objects.create(
            equipment=self.equipment,
            last_maintenance_day=self.last_maintenance,
            next_maintenance_day=self.next_maintenance,
            status="on_track",
        )
        self.assertEqual(maintenance.next_maintenance_in_days(), 60)

    def test_is_expired_true(self):
        expired_maintenance = Maintenance.objects.create(
            equipment=self.equipment,
            last_maintenance_day=self.last_maintenance,
            next_maintenance_day=self.today - timedelta(days=1),
            status="expired",
        )
        self.assertTrue(expired_maintenance.is_expired())

    def test_is_expired_false(self):
        active_maintenance = Maintenance.objects.create(
            equipment=self.equipment,
            last_maintenance_day=self.last_maintenance,
            next_maintenance_day=self.next_maintenance,
            status="on_track",
        )
        self.assertFalse(active_maintenance.is_expired())