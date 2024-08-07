# Generated by Django 5.0.6 on 2024-07-11 06:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_paperreference'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pubmedindex',
            options={'ordering': ['-source', '-index']},
        ),
        migrations.AlterField(
            model_name='pubmedindex',
            name='doi',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='pubmedindex',
            name='pmid',
            field=models.BigIntegerField(blank=True, db_index=True, null=True),
        ),
    ]
