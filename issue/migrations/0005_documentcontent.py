# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0042_auto_20170919_1624'),
        ('issue', '0004_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('order', models.IntegerField(default=1)),
                ('comments', models.TextField(blank=True)),
                ('status', models.CharField(default=b'proposed', max_length=32, choices=[(b'proposed', 'Proposed'), (b'accepted', 'Accepted'), (b'rejected', 'Rejected'), (b'deprecated', 'Deprecated')])),
                ('document', models.ForeignKey(to='core.Document')),
                ('predecessor', models.ForeignKey(blank=True, to='issue.DocumentContent', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
