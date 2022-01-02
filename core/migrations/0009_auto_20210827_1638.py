# Generated by Django 2.2.24 on 2021-08-27 16:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('core', '0008_auto_20210116_2004'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
        ),
        migrations.AlterField(
            model_name='event',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.User'),
        ),
    ]