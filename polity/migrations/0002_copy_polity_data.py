# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_polities(apps, schema_editor):
    OldPolity = apps.get_model('core', 'Polity')
    NewPolity = apps.get_model('polity', 'Polity')

    simply_copied_fields = [
        'name',
        'slug',
        'description',
        'created_by',
        'modified_by',
        'created',
        'modified',
        'is_listed',
        'is_nonmembers_readable',
        'is_newissue_only_officers',
        'is_front_polity',
    ]

    multi_fields = [
        'members',
        'officers',
        'polityruleset_set',
        'topic_set',
        'issue_set',
        'document_set',
        'election_set',

        'remote_election_votes',
        'remote_election_candidates',
    ]

    old_polities = OldPolity.objects.order_by('id')
    for op in old_polities:
        np = NewPolity()

        # Need to save right away to get special auto-populated fields to do
        # their things before we override them with old data. Therefore we
        # also need to set the ID immediately, so that we can find the
        # appropriate item later.
        np.id = op.id
        np.save()

        for fieldname in simply_copied_fields:
            setattr(np, fieldname, getattr(op, fieldname))

        # Need to save before adding anything to ManyToMany-fields.
        np.save()

        for fieldname in multi_fields:
            for value in getattr(op, fieldname).all():
                getattr(np, fieldname).add(value)

    # Process the parent polities. We iterate again because we need to make
    # sure that all the new polities exist first. Also, this is a special
    # process because we need to get the new polity.Polity object and not the
    # old core.Polity object.
    for op in old_polities:
        if op.parent:
            np = NewPolity.objects.get(id=op.id)
            np.parent = NewPolity.objects.get(id=op.parent_id)
            np.save()


class Migration(migrations.Migration):

    dependencies = [
        ('polity', '0001_initial'),
        ('core', '0020_auto_20170907_1944'),
        ('election', '0003_auto_20170907_1944'),
    ]

    operations = [
        migrations.RunPython(copy_polities)
    ]

