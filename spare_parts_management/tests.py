from decimal import Decimal
from django.test import TestCase
from tb2_vsm.models import Location
from .models import Producer, Buyer, BackupEquipment


class ProducerModelTests(TestCase):
    def test_str_method_returns_name(self):
        producer = Producer.objects.create(
            name="Test Producer", telephone="123456789", email="prod@example.com"
        )
        self.assertEqual(str(producer), "Test Producer")


class BuyerModelTests(TestCase):
    def test_str_method_returns_full_name(self):
        buyer = Buyer.objects.create(full_name="Jane Doe", email="jane@example.com")
        self.assertEqual(str(buyer), "Jane Doe")


class BackupEquipmentModelTests(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            country="DE", supplier_name="Supplier A"
        )
        self.producer = Producer.objects.create(
            name="Producer X", telephone="123456789", email="producerx@example.com"
        )
        self.buyer = Buyer.objects.create(
            full_name="Buyer Y", email="buyery@example.com"
        )

    def test_status_critical_when_current_quantity_zero(self):
        be = BackupEquipment.objects.create(
            name="Equipment 1",
            minimum_quantity=10,
            current_quantity=0,
            location=self.location,
            producer=self.producer,
            buyer=self.buyer,
        )
        self.assertEqual(be.status, "Critical")

    def test_status_low_when_current_quantity_below_minimum(self):
        be = BackupEquipment.objects.create(
            name="Equipment 2",
            minimum_quantity=10,
            current_quantity=5,
            location=self.location,
            producer=self.producer,
            buyer=self.buyer,
        )
        self.assertEqual(be.status, "Low")

    def test_status_stable_when_current_quantity_equal_or_above_minimum(self):
        be = BackupEquipment.objects.create(
            name="Equipment 3",
            minimum_quantity=10,
            current_quantity=10,
            location=self.location,
            producer=self.producer,
            buyer=self.buyer,
        )
        self.assertEqual(be.status, "Stable")

        be.current_quantity = 15
        be.save()
        self.assertEqual(be.status, "Stable")

    def test_str_method_returns_name_and_location_supplier(self):
        be = BackupEquipment.objects.create(
            name="Equipment 4",
            minimum_quantity=10,
            current_quantity=20,
            location=self.location,
            producer=self.producer,
            buyer=self.buyer,
        )
        expected_str = f"Equipment 4 ({self.location.supplier_name})"
        self.assertEqual(str(be), expected_str)
