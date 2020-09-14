# Generated by Django 2.2.7 on 2020-09-14 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polity', '0006_auto_20200909_2020'),
    ]

    operations = [
        migrations.AddField(
            model_name='polity',
            name='name_short',
            field=models.CharField(default='', help_text='Optional. Could be an abbreviation or acronym, for example.', max_length=30, verbose_name='Short name'),
        ),
    ]
