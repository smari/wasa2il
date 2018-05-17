from wasa2il.forms import Wasa2ilForm

from polity.models import Polity

class PolityForm(Wasa2ilForm):
    class Meta:
        model = Polity
        exclude = ('slug', 'parent', 'members')
