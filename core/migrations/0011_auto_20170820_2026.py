# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20170817_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentcontent',
            name='status',
            field=models.CharField(default=b'proposed', max_length=32, choices=[(b'proposed', 'Proposed'), (b'accepted', 'Accepted'), (b'rejected', 'Rejected'), (b'deprecated', 'Deprecated')]),
        ),
        migrations.AlterField(
            model_name='issue',
            name='special_process',
            field=models.CharField(default=b'', choices=[(b'accepted_at_assembly', 'Accepted at assembly'), (b'rejected_at_assembly', 'Rejected at assembly')], max_length=32, blank=True, null=True, verbose_name='Special process'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='displayname',
            field=models.CharField(help_text='The name to display on the site.', max_length=255, null=True, verbose_name='Name', blank=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default=b'is', max_length=6, verbose_name='Language', choices=[(b'is', b'\xc3\x8dslenska'), (b'en', b'English'), (b'es', b'Espa\xc3\xb1ol'), (b'fr', b'Fran\xc3\xa7aise'), (b'nl', b'Nederlands')]),
        ),
    ]
