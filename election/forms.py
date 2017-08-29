from django.forms import ModelForm

from election.models import Election


class ElectionForm(ModelForm):
    class Meta:
        model = Election
        exclude = ('polity', 'slug', 'is_processed')
