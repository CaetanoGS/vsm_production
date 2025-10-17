from decimal import Decimal
from django.forms import ValidationError
from django.test import TestCase
from tb2_vsm.models import (
    TonieboxProduction,
    Process,
    Step,
    Location,
    FactoryCloud,
    Equipment,
)
from django_countries.fields import Country


class LocationModelTests(TestCase):
    def test_str_returns_supplier_and_country(self):
        loc = Location.objects.create(country="DE", supplier_name="Supplier A")
        self.assertEqual(str(loc), "Supplier A (DE)")


class StepModelTests(TestCase):
    def setUp(self):
        self.process = Process.objects.create(name="Assembly")

    def test_str_returns_name_or_default(self):
        step1 = Step.objects.create(process=self.process, name="Step 1")
        step2 = Step.objects.create(process=self.process, name=None)
        self.assertEqual(str(step1), "Step 1")
        self.assertEqual(str(step2), "Unnamed Step")

    def test_calculate_output_per_hour(self):
        step = Step(cycle_time=Decimal("60.00"))
        self.assertEqual(step.calculate_output_per_hour(), 60)  # 3600/60 = 60

        step.cycle_time = None
        self.assertEqual(step.calculate_output_per_hour(), 0)

    def test_save_sets_output_per_hour(self):
        step = Step.objects.create(
            process=self.process,
            cycle_time=Decimal("30.00"),
            amount_of_operators=2,
        )
        self.assertEqual(step.output_per_hour, Decimal("120"))  # 3600 / 30 = 120


class ProcessModelTests(TestCase):
    def setUp(self):
        self.process = Process.objects.create(name="Packaging")

    def test_str_returns_name_or_default(self):
        p1 = Process.objects.create(name="Process 1")
        p2 = Process.objects.create(name=None)
        self.assertEqual(str(p1), "Process 1")
        self.assertEqual(str(p2), "Unnamed Process")

    def test_total_operators(self):
        Step.objects.create(process=self.process, amount_of_operators=2)
        Step.objects.create(process=self.process, amount_of_operators=3)
        self.assertEqual(self.process.total_operators(), 5)

    def test_average_cycle_time(self):
        Step.objects.create(process=self.process, cycle_time=Decimal("10"))
        Step.objects.create(process=self.process, cycle_time=Decimal("20"))
        Step.objects.create(process=self.process, cycle_time=None)
        self.assertEqual(self.process.average_cycle_time(), 15.0)

    def test_minimum_output_per_hour(self):
        self.process.steps.all().delete()

        Step.objects.create(process=self.process, name="Step 1", cycle_time=72)
        Step.objects.create(process=self.process, name="Step 2", cycle_time=120)
        Step.objects.create(process=self.process, name="Step 3", cycle_time=90)

        self.assertEqual(self.process.minimum_output_per_hour(), Decimal("30.00"))

    def test_default_ordering_by_order_field(self):
        p1 = Process.objects.create(name="Process 1", order=2)
        p2 = Process.objects.create(name="Process 2", order=1)
        p3 = Process.objects.create(name="Process 3", order=3)

        processes = list(
            Process.objects.filter(id__in=[p1.id, p2.id, p3.id]).order_by("order")
        )

        self.assertEqual(processes, [p2, p1, p3])


class TonieboxProductionModelTests(TestCase):
    def setUp(self):
        self.loc = Location.objects.create(country="US", supplier_name="Loc1")
        self.process1 = Process.objects.create(name="Proc1")
        self.process2 = Process.objects.create(name="Proc2")

        Step.objects.create(
            process=self.process1,
            cycle_time=Decimal("10"),
            amount_of_operators=1,
            output_per_hour=Decimal("360"),
        )
        Step.objects.create(
            process=self.process1,
            cycle_time=Decimal("20"),
            amount_of_operators=2,
            output_per_hour=Decimal("180"),
        )
        Step.objects.create(
            process=self.process2,
            cycle_time=Decimal("15"),
            amount_of_operators=1,
            output_per_hour=Decimal("240"),
        )

        self.prod = TonieboxProduction.objects.create(
            name="Batch 1", location=self.loc, category=TonieboxProduction.TONIES
        )
        self.prod.processes.add(self.process1, self.process2)

    def test_str_returns_name_or_default(self):
        p = TonieboxProduction.objects.create(name="TestProd")
        self.assertEqual(str(p), "TestProd")
        p2 = TonieboxProduction.objects.create(name=None)
        self.assertEqual(str(p2), f"Toniebox Production {p2.id}")

    def test_total_operators(self):
        self.assertEqual(self.prod.total_operators(), 4)  # 1+2+1 from steps

    def test_average_cycle_time(self):
        # average of (10, 20, 15) = 15.0
        self.assertEqual(self.prod.average_cycle_time(), 15.0)

    def test_minimum_output_per_hour(self):
        # min of (360, 180, 240) = 180
        self.assertEqual(self.prod.minimum_output_per_hour(), 180)


class FactoryCloudModelTests(TestCase):
    def setUp(self):
        self.loc = Location.objects.create(country="FR", supplier_name="Loc2")

    def test_str_and_name_auto_set(self):
        fc = FactoryCloud.objects.create(
            fc_id=10, url="http://example.com", location=self.loc
        )
        self.assertEqual(fc.name, "Factory Cloud 10")
        self.assertEqual(str(fc), "Factory Cloud 10")

        fc2 = FactoryCloud.objects.create(
            fc_id=20, name="Custom Name", url="http://example.com", location=self.loc
        )
        self.assertEqual(fc2.name, "Custom Name")
        self.assertEqual(str(fc2), "Custom Name")


class EquipmentModelTests(TestCase):
    def setUp(self):
        self.loc = Location.objects.create(country="IT", supplier_name="Loc3")

    def test_str_returns_name_or_category_and_serial(self):
        eq = Equipment.objects.create(
            category=Equipment.LASER_MARKER,
            name="Laser1",
            location=self.loc,
        )
        self.assertEqual(str(eq), "Laser1")

        eq2 = Equipment.objects.create(
            category=Equipment.COMPUTER,
            name=None,
            location=self.loc,
        )
        self.assertEqual(str(eq2), "Computer")

    def test_save_sets_active_based_on_backup(self):
        eq = Equipment.objects.create(
            category=Equipment.SDR, backup=True, location=self.loc
        )
        self.assertFalse(eq.active)

        eq.backup = False
        eq.save()
        self.assertTrue(eq.active)

    def test_production_category_is_set_correctly(self):
        eq = Equipment.objects.create(
            category=Equipment.JIG,
            production_type=Equipment.TONIEBOX_2,
            location=self.loc,
        )
        self.assertEqual(eq.production_type, Equipment.TONIEBOX_2)

    def test_production_category_can_be_blank(self):
        eq = Equipment.objects.create(
            category=Equipment.SWITCH,
            production_type=None,
            location=self.loc,
        )
        self.assertIsNone(eq.production_type)

    def test_invalid_production_category(self):
        eq = Equipment(
            category=Equipment.CAMERA,
            production_type="InvalidCategory",
            location=self.loc,
        )
        with self.assertRaisesMessage(ValidationError, "is not a valid choice"):
            eq.full_clean()

    def test_quantity_field_default_and_custom_value(self):
        eq_default = Equipment.objects.create(
            category=Equipment.UPS,
            location=self.loc,
        )
        self.assertEqual(eq_default.quantity, 0)

        eq_custom = Equipment.objects.create(
            category=Equipment.UPS,
            location=self.loc,
            quantity=5,
        )
        self.assertEqual(eq_custom.quantity, 5)
