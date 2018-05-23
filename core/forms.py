# -*- coding: utf-8 -*-
from django.forms import CharField
from django.forms import EmailField
from django.forms import TypedChoiceField
from django.forms import ValidationError
from django.forms.widgets import ChoiceWidget
from django.utils.translation import ugettext as _

from registration.forms import RegistrationForm

from wasa2il.forms import Wasa2ilForm
from prosemirror.widgets import ProseMirrorWidget

from core.models import UserProfile

# FIXME/TODO: When a user changes email addresses, there is currently no
# functionality to verify the new email address. Therefore, the email field is
# disabled in UserProfileForm until that functionality has been implemented.

class EmailWantedField(ChoiceWidget):
    template_name = 'forms/widgets/email_wanted.html'


class UserProfileForm(Wasa2ilForm):
    #email = EmailField(label=_("E-mail"), help_text=_("The email address you'd like to use for the site."))
    bio = CharField(label=_('Bio'), widget=ProseMirrorWidget, required=False)

    class Meta:
        model = UserProfile
        #fields = ('displayname', 'email', 'picture', 'bio', 'language')
        fields = ('displayname', 'picture', 'bio', 'language')

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


class Wasa2ilRegistrationForm(RegistrationForm):
    email_wanted = TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=EmailWantedField,
        label=_('Consent for sending email')
    )
