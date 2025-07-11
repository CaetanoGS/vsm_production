# Generated by Django 5.2.1 on 2025-06-26 06:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tb2_vsm", "0005_step_updated_at"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="equipment",
            name="serial_number",
        ),
        migrations.AddField(
            model_name="equipment",
            name="serial_numbers_array",
            field=models.JSONField(
                blank=True, default=list, verbose_name="Serial Numbers"
            ),
        ),
        migrations.CreateModel(
            name="EquipmentSerial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("serial_number", models.CharField(max_length=100, unique=True)),
                (
                    "equipment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="serials",
                        to="tb2_vsm.equipment",
                    ),
                ),
            ],
        ),
    ]
