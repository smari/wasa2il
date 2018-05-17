# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('polity', '0003_polityruleset'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('issue', '0009_auto_20170919_1638'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('slug', models.SlugField(max_length=128, blank=True)),
                ('is_adopted', models.BooleanField(default=False)),
                ('is_proposed', models.BooleanField(default=False)),
                ('issues', models.ManyToManyField(to='issue.Issue')),
                ('polity', models.ForeignKey(to='polity.Polity')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
        migrations.AddField(
            model_name='documentcontent',
            name='new_document',
            field=models.ForeignKey(to='issue.Document', null=True),
        ),
    ]
