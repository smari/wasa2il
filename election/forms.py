from wasa2il.forms import Wasa2ilForm

from election.models import Election


class ElectionForm(Wasa2ilForm):
    class Meta:
        model = Election
        exclude = ('polity', 'slug', 'is_processed', 'stats')
