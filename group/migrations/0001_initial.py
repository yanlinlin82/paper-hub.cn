# Generated by Django 4.2.4 on 2023-08-12 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=100)),
                ('desc', models.CharField(default='', max_length=2000)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
