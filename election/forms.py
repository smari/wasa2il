from django.forms import ModelForm
from django.conf import settings

from datetimewidget.widgets import DateTimeWidget

from election.models import Election


class ElectionForm(ModelForm):
    class Meta:
        model = Election
        dateTimeOptions = {
            'format': settings.DATETIME_FORMAT_DJANGO_WIDGET,
            'autoclose': True,
        }
        widgets = {
            'deadline_candidacy': DateTimeWidget(options=dateTimeOptions, bootstrap_version=3),
            'starttime_votes': DateTimeWidget(options=dateTimeOptions, bootstrap_version=3),
            'deadline_votes': DateTimeWidget(options=dateTimeOptions, bootstrap_version=3),
            'deadline_joined_org': DateTimeWidget(options=dateTimeOptions, bootstrap_version=3),
        }
        exclude = ('polity', 'slug', 'is_processed', 'stats')
