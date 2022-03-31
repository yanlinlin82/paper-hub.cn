# Generated by Django 4.0.3 on 2022-03-31 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0003_paper_is_favorite_paper_is_preprint'),
    ]

    operations = [
        migrations.AddField(
            model_name='label',
            name='desc',
            field=models.CharField(default='', max_length=2000),
        ),
        migrations.AddField(
            model_name='label',
            name='owner',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='label',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='weixin_id',
            field=models.CharField(default='', max_length=100),
        ),
    ]
