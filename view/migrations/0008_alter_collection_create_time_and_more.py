# Generated by Django 4.0.4 on 2022-06-05 14:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0007_paper_delete_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='update_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='pub_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='paper',
            name='update_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_login_time',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
