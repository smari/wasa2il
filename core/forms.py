# -*- coding: utf-8 -*-
from django.forms import Form
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


class EmailWantedField(ChoiceWidget):
    template_name = 'forms/widgets/email_wanted.html'


class UserProfileForm(Wasa2ilForm):
    email = EmailField(label=_("E-mail"), help_text=_("You can change your email address, but will then need to verify it."))
    bio = CharField(label=_('Bio'), widget=ProseMirrorWidget, required=False)
    declaration_of_interests = CharField(
        label=_('Declaration of interests'),
        widget=ProseMirrorWidget,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ('displayname', 'email', 'picture', 'bio', 'declaration_of_interests', 'language', 'email_wanted')

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
            else:
                ext = picture.name.split('.')[-1].lower()
                allowed_exts = ['jpg', 'jpeg', 'png', 'gif']
                if ext not in allowed_exts:
                    raise ValidationError(u'%s: %s' % (
                        _('Only the following file endings are allowed'),
                        ', '.join(allowed_exts)
                    ))

        return data


class Wasa2ilRegistrationForm(RegistrationForm):
    email_wanted = TypedChoiceField(
        choices=((True, _('Yes')), (False, _('No'))),
        widget=EmailWantedField,
        label=_('Consent for sending email')
    )

class PushNotificationForm(Form):
    text = CharField(label=_('Message'))
