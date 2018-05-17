# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def copy_old_data_to_new(apps, schema_editor):
    OldModel = apps.get_model('core', 'Document')
    NewModel = apps.get_model('issue', 'Document')

    simply_copied_fields = [
        'name',
        'slug',
        'is_adopted',
        'is_proposed',
    ]

    simply_copied_fields_needed_at_creation = [
        'user',
        'polity',
    ]

    multi_fields = [
        'documentcontent_set',
        'issues',
    ]

    old_objects = OldModel.objects.order_by('id')
    for old_object in old_objects:
        kwargs = {}
        for fieldname in simply_copied_fields_needed_at_creation:
            kwargs[fieldname] = getattr(old_object, fieldname)
        new_object = NewModel(**kwargs)

        # Need to save right away to get special auto-populated fields to do
        # their things before we override them with old data. Therefore we
        # also need to set the ID immediately, so that we can find the
        # appropriate item later.
        new_object.id = old_object.id
        new_object.save()

        for fieldname in simply_copied_fields:
            if hasattr(old_object, fieldname):
                setattr(new_object, fieldname, getattr(old_object, fieldname))

        # Need to save before adding anything to ManyToMany-fields.
        new_object.save()

        for fieldname in multi_fields:
            for value in getattr(old_object, fieldname).all():
                getattr(new_object, fieldname).add(value)

    # Process the parent objects, if available. We iterate again because we
    # need to make sure that all the new objects exist first. Also, this is a
    # special process because we need to get the new [new_app].[model] object
    # and not the old [old_app].[model] object.
    for old_object in old_objects:
        if hasattr(old_object, 'parent'):
            if old_object.parent:
                new_object = NewModel.objects.get(id=old_object.id)
                new_object.parent = NewModel.objects.get(id=old_object.parent_id)
                new_object.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20170922_1500'),
        ('issue', '0010_auto_20170922_1544'),
    ]

    operations = [
        migrations.RunPython(copy_old_data_to_new),
    ]
