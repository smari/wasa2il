from django.forms import ModelForm

from polity.models import Polity

class PolityForm(ModelForm):
    class Meta:
        model = Polity
        exclude = ('slug', 'parent', 'members')

