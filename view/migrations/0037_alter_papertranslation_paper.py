# Generated by Django 5.0.6 on 2024-07-02 03:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0036_remove_recommendation_trackings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='papertranslation',
            name='paper',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='translation', to='view.paper'),
        ),
    ]