# Generated by Django 5.0.7 on 2024-08-01 16:40

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_paper_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaperChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('chat_request', models.CharField(blank=True, default='', max_length=1048576)),
                ('response_time', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('chat_response', models.CharField(blank=True, default='', max_length=1048576)),
                ('paper', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='chat_summary', to='core.paper')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.userprofile')),
            ],
        ),
    ]
