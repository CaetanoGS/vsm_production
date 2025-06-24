from django.core.exceptions import ValidationError
from django.test import TestCase
from tb2_vsm.models import Location
from .models import Producer, Buyer, BackupEquipment


class ProducerModelTests(TestCase):
    def test_str_method_returns_name(self):
        producer = Producer.objects.create(
            name="Test Producer", telephone="123456789", email="prod@example.com"
        )
        self.assertEqual(str(producer), "Test Producer")

    def test_optional_fields_can_be_blank(self):
        producer = Producer.objects.create(name="Optional Fields Producer")
        self.assertEqual(producer.name, "Optional Fields Producer")
        self.assertIsNone(producer.telephone)
        self.assertIsNone(producer.email)
        self.assertIsNone(producer.ticket_system)

    def test_ticket_system_accepts_url(self):
        url = "https://tickets.example.com"
        producer = Producer.objects.create(
            name="With Ticket System", ticket_system=url
        )
        self.assertEqual(producer.ticket_system, url)


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

    def create_backup_equipment(self, **kwargs):
        default_data = {
            "name": "Test Equipment",
            "minimum_quantity": 10,
            "current_quantity": 5,
            "location": self.location,
            "producer": self.producer,
            "buyer": self.buyer,
        }
        default_data.update(kwargs)
        return BackupEquipment.objects.create(**default_data)

    def test_status_critical_when_current_quantity_zero(self):
        be = self.create_backup_equipment(current_quantity=0)
        self.assertEqual(be.status, "Critical")

    def test_status_low_when_current_quantity_below_minimum(self):
        be = self.create_backup_equipment(current_quantity=5)
        self.assertEqual(be.status, "Low")

    def test_status_stable_when_current_quantity_equal_or_above_minimum(self):
        be = self.create_backup_equipment(current_quantity=10)
        self.assertEqual(be.status, "Stable")

        be.current_quantity = 15
        be.save()
        self.assertEqual(be.status, "Stable")

    def test_str_method_returns_name_and_location_supplier(self):
        be = self.create_backup_equipment(name="UPS Unit")
        expected_str = f"UPS Unit ({self.location.supplier_name})"
        self.assertEqual(str(be), expected_str)

    def test_category_defaults_to_toniebox_2(self):
        be = self.create_backup_equipment()
        self.assertEqual(be.category, BackupEquipment.TONIEBOX_2)

    def test_setting_valid_category_choices(self):
        valid_categories = [choice[0] for choice in BackupEquipment.CATEGORY_CHOICES]
        for category in valid_categories:
            be = self.create_backup_equipment(category=category)
            self.assertEqual(be.category, category)

    def test_invalid_category_raises_error(self):
        be = self.create_backup_equipment()
        be.category = "InvalidCategory"
        with self.assertRaises(ValidationError):
            be.full_clean()
