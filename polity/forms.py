from wasa2il.forms import Wasa2ilForm

from polity.models import Polity

class PolityForm(Wasa2ilForm):
    class Meta:
        model = Polity
        exclude = ('slug', 'parent', 'members', 'officers', 'wranglers')


class PolityOfficersForm(Wasa2ilForm):
    class Meta:
        model = Polity
        fields = ('officers',)
