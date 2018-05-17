from django.forms import EmailField, CharField
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from wasa2il.forms import Wasa2ilForm
from prosemirror.widgets import ProseMirrorWidget

from core.models import UserProfile


class UserProfileForm(Wasa2ilForm):
    email = EmailField(label=_("E-mail"), help_text=_("The email address you'd like to use for the site."))
    bio = CharField(widget=ProseMirrorWidget)

    class Meta:
        model = UserProfile
        fields = ('displayname', 'email', 'picture', 'bio', 'language')

    # We need to keep the 'request' object for certain kinds of validation ('picture' in this case)
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserProfileForm, self).__init__(*args, **kwargs)

    def clean_picture(self):
        data = self.cleaned_data['picture']

        picture = self.request.FILES.get('picture')
        if picture:
            if picture.name.find('.') == -1:
                raise ValidationError(_('Filename must contain file extension'))

        return data
