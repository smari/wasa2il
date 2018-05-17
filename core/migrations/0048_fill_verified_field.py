# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


def fill_userprofile_verified_field(apps, schema_editor):
    UserProfile = apps.get_model('core', 'UserProfile')
    for profile in UserProfile.objects.select_related('user').all():
        # UserProfile's overridden save method does this automatically, but
        # since overridden save methods are not called in migrations, we must
        # specifically configure this here for existing data. UserProfile's
        # save method takes care of this from now on.
        if hasattr(settings, 'SAML_1'):
            profile.verified = all((
                profile.verified_ssn is not None and len(profile.verified_ssn) > 0,
                profile.verified_name is not None and len(profile.verified_name) > 0
            ))
        else:
            profile.verified = profile.user.is_active

        profile.save()


def unfill_userprofile_verified_field(apps, schema_editor):
    # Do nothing. Only here so that migration can be unmigrated.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0047_userprofile_verified'),
    ]

    operations = [
        migrations.RunPython(
            fill_userprofile_verified_field,
            unfill_userprofile_verified_field
        )
    ]
