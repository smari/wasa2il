# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import migrations, models

def reset_user_language_preference(apps, schema_editor):
    User = apps.get_model('core', 'userprofile')
    for user in User.objects.all():
        user.language = settings.LANGUAGE_CODE
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_polity_location_codes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='language',
            field=models.CharField(default=settings.LANGUAGE_CODE, max_length=b'6', verbose_name='Language', choices=settings.LANGUAGES),
        ),
        migrations.RunPython(reset_user_language_preference),
    ]
