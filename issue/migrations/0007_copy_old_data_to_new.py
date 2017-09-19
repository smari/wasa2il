# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def copy_old_data_to_new(apps, schema_editor):
    OldModel = apps.get_model('core', 'DocumentContent')
    NewModel = apps.get_model('issue', 'DocumentContent')

    simply_copied_fields = [
        'created',
        'text',
        'order',
        'comments',
        'status',
    ]

    simply_copied_fields_needed_at_creation = [
        'user',
        'document',
    ]

    multi_fields = [
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
        if hasattr(old_object, 'predecessor'):
            if old_object.predecessor:
                new_object = NewModel.objects.get(id=old_object.id)
                new_object.predecessor = NewModel.objects.get(id=old_object.predecessor_id)
                new_object.save()


def copy_documentcontents_of_issues(apps, schema_editor):
    Issue = apps.get_model('issue', 'Issue')

    for issue in Issue.objects.all():
        issue.new_documentcontent_id = issue.documentcontent_id
        issue.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_auto_20170919_1624'),
        ('issue', '0006_issue_new_documentcontent'),
    ]

    operations = [
        migrations.RunPython(copy_old_data_to_new),
        migrations.RunPython(copy_documentcontents_of_issues),
    ]
