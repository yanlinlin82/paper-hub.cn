# Generated by Django 5.0.6 on 2024-07-01 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0024_userprofile_wx_unionid'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Paper',
            new_name='Review',
        ),
    ]
