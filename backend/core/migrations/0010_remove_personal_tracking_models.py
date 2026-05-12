from django.db import migrations


def vacuum_sqlite_db(apps, schema_editor):
    if schema_editor.connection.vendor != 'sqlite':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('VACUUM')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('core', '0009_delete_pubmedindex'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PaperChat',
        ),
        migrations.DeleteModel(
            name='PaperTracking',
        ),
        migrations.DeleteModel(
            name='Recommendation',
        ),
        migrations.RunPython(vacuum_sqlite_db, migrations.RunPython.noop),
    ]
