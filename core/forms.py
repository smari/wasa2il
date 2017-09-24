from django.forms import ModelForm
from django.forms import EmailField
from django.forms import ValidationError
from django.utils.translation import ugettext as _

from core.models import UserProfile


class UserProfileForm(ModelForm):
    email = EmailField(label=_("E-mail"), help_text=_("The email address you'd like to use for the site."))

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
