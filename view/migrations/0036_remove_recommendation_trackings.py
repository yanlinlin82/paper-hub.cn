# Generated by Django 5.0.6 on 2024-07-02 00:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0035_recommendationdetails'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recommendation',
            name='trackings',
        ),
    ]