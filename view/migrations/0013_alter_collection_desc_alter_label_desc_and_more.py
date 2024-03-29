# Generated by Django 4.2.5 on 2023-09-22 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('view', '0012_user_auth_user_user_wx_openid_user_wx_unionid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='desc',
            field=models.CharField(blank=True, default='', max_length=50000),
        ),
        migrations.AlterField(
            model_name='label',
            name='desc',
            field=models.CharField(blank=True, default='', max_length=2000),
        ),
        migrations.AlterField(
            model_name='label',
            name='owner',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='paper',
            name='abstract',
            field=models.CharField(blank=True, default='', max_length=4000),
        ),
        migrations.AlterField(
            model_name='paper',
            name='arxiv_id',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='paper',
            name='authors',
            field=models.CharField(blank=True, default='', max_length=4000),
        ),
        migrations.AlterField(
            model_name='paper',
            name='cnki_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='paper',
            name='comments',
            field=models.CharField(blank=True, default='', max_length=65536),
        ),
        migrations.AlterField(
            model_name='paper',
            name='doi',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='paper',
            name='full_text',
            field=models.FileField(blank=True, default='', upload_to=''),
        ),
        migrations.AlterField(
            model_name='paper',
            name='journal',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='paper',
            name='keywords',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='paper',
            name='pmcid',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='paper',
            name='pmid',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='paper',
            name='urls',
            field=models.CharField(blank=True, default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='weixin_id',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='wx_openid',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='user',
            name='wx_unionid',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
