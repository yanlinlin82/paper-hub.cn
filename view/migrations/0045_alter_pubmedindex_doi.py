# Generated by Django 5.0.6 on 2024-07-06 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0044_pubmedindex'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pubmedindex',
            name='doi',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True, unique=True),
        ),
    ]