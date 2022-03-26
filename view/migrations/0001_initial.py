# Generated by Django 4.0.3 on 2022-03-26 16:16

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('nickname', models.CharField(max_length=100)),
                ('weixin_id', models.CharField(max_length=100)),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_login_time', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('doi', models.CharField(default='', max_length=100)),
                ('pmid', models.CharField(default='', max_length=20)),
                ('pmcid', models.CharField(default='', max_length=100)),
                ('arxiv_id', models.CharField(default='', max_length=100)),
                ('journal', models.CharField(default='', max_length=200)),
                ('publish_year', models.CharField(default='', max_length=10)),
                ('pub_date', models.DateField(default=datetime.date.today)),
                ('title', models.CharField(default='', max_length=500)),
                ('comments', models.CharField(default='', max_length=65536)),
                ('authors', models.CharField(default='', max_length=65536)),
                ('abstract', models.CharField(default='', max_length=65536)),
                ('urls', models.CharField(default='', max_length=65536)),
                ('is_private', models.BooleanField(default=True)),
                ('full_text', models.FileField(default='', upload_to='')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='view.user')),
                ('labels', models.ManyToManyField(to='view.label')),
            ],
        ),
    ]
