from django.db import migrations

def update_equipment_active_status(apps, schema_editor):
    Equipment = apps.get_model('tb2_vsm', 'Equipment')

    # Set active=False where backup=True
    Equipment.objects.filter(backup=True).update(active=False)

    # Set active=True where backup=False or null
    Equipment.objects.filter(backup=False).update(active=True)
    Equipment.objects.filter(backup__isnull=True).update(active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('tb2_vsm', '0010_factorycloud'),
    ]

    operations = [
        migrations.RunPython(update_equipment_active_status),
    ]
