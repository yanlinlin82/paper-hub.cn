# Generated by Django 5.0.6 on 2024-07-09 01:51

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomCheckInInterval',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('deadline', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=128)),
                ('color', models.CharField(default='#B6CFF5', max_length=7)),
                ('desc', models.CharField(default='', max_length=2000)),
            ],
        ),
        migrations.CreateModel(
            name='Paper',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField()),
                ('update_time', models.DateTimeField()),
                ('title', models.CharField(db_index=True, default='', max_length=4096)),
                ('journal', models.CharField(blank=True, db_index=True, default='', max_length=256)),
                ('pub_date', models.CharField(blank=True, default='', max_length=64)),
                ('pub_year', models.IntegerField(blank=True, db_index=True, default=None, null=True)),
                ('authors', models.CharField(blank=True, default='', max_length=1048576)),
                ('affiliations', models.CharField(blank=True, default='', max_length=1048576)),
                ('abstract', models.CharField(blank=True, default='', max_length=1048576)),
                ('keywords', models.CharField(blank=True, default='', max_length=1048576)),
                ('urls', models.CharField(blank=True, default='', max_length=1048576)),
                ('doi', models.CharField(blank=True, db_index=True, default='', max_length=128)),
                ('pmid', models.CharField(blank=True, db_index=True, default='', max_length=128)),
                ('arxiv_id', models.CharField(blank=True, db_index=True, default='', max_length=128)),
                ('pmcid', models.CharField(blank=True, db_index=True, default='', max_length=128)),
                ('cnki_id', models.CharField(blank=True, db_index=True, default='', max_length=128)),
                ('language', models.CharField(default='eng', max_length=20)),
            ],
            options={
                'ordering': ['-create_time'],
            },
        ),
        migrations.CreateModel(
            name='PaperTranslation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_cn', models.CharField(blank=True, default='', max_length=4096)),
                ('abstract_cn', models.CharField(blank=True, default='', max_length=65536)),
                ('paper', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='translation', to='core.paper')),
            ],
        ),
        migrations.CreateModel(
            name='PubMedIndex',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.IntegerField()),
                ('index', models.IntegerField()),
                ('doi', models.CharField(blank=True, db_index=True, max_length=128, null=True, unique=True)),
                ('pmid', models.BigIntegerField(blank=True, db_index=True, null=True, unique=True)),
            ],
            options={
                'indexes': [models.Index(fields=['doi'], name='core_doi_idx'), models.Index(fields=['pmid'], name='core_pmid_idx')],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField()),
                ('nickname', models.CharField(blank=True, default='', max_length=100)),
                ('wx_openid', models.CharField(blank=True, default='', max_length=100)),
                ('wx_unionid', models.CharField(blank=True, default='', max_length=100)),
                ('debug_mode', models.BooleanField(default=False)),
                ('auth_user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField()),
                ('update_time', models.DateTimeField()),
                ('delete_time', models.DateTimeField(default=None, null=True)),
                ('comment', models.CharField(blank=True, default='', max_length=1048576)),
                ('labels', models.ManyToManyField(blank=True, related_name='reviews', to='core.label')),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paper')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField()),
                ('read_time', models.DateTimeField(db_index=True, default=None, null=True)),
                ('source', models.CharField(default='', max_length=100)),
                ('labels', models.ManyToManyField(blank=True, related_name='recommendations', to='core.label')),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.paper')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='PaperTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='read', max_length=20)),
                ('value', models.CharField(blank=True, default='', max_length=100)),
                ('memo', models.CharField(blank=True, default='', max_length=2000)),
                ('label', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.label')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.userprofile')),
            ],
        ),
        migrations.AddField(
            model_name='label',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.userprofile'),
        ),
        migrations.CreateModel(
            name='GroupProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=64)),
                ('display_name', models.CharField(default='', max_length=128)),
                ('desc', models.CharField(default='', max_length=2000)),
                ('create_time', models.DateTimeField()),
                ('reviews', models.ManyToManyField(to='core.review')),
                ('members', models.ManyToManyField(to='core.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=255)),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('created_at', models.DateTimeField()),
                ('expires_at', models.DateTimeField()),
                ('client_type', models.CharField(choices=[('website', '网页端'), ('weixin', '微信小程序')], max_length=10)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='UserAlias',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alias_for', to='core.userprofile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='primary', to='core.userprofile')),
            ],
            options={
                'unique_together': {('user', 'alias')},
            },
        ),
    ]
