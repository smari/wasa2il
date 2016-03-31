from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User, check_password
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext, ugettext_lazy as _

class PiratePartyMemberAuthenticationBackend(ModelBackend):

    def authenticate(self, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

class PiratePartyMemberAuthenticationForm(AuthenticationForm):
    email = forms.CharField(label=_("E-mail"), max_length=30)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        self.fields.pop('username') # Remove field inherited from superclass
        self.fields.insert(0, 'email', self.fields['email']) # set form field order

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'])
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        self.check_for_test_cookie()
        return self.cleaned_data

