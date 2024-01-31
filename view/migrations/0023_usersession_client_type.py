# Generated by Django 5.0 on 2024-01-31 02:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0022_useralias'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersession',
            name='client_type',
            field=models.CharField(choices=[('website', '网页端'), ('weixin', '微信小程序')], default='weixin', max_length=10),
            preserve_default=False,
        ),
    ]
