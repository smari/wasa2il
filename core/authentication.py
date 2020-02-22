from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext, ugettext_lazy as _


class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return None

        user = self.custom_get_user(username)
        if user and user.check_password(password):
            return user
        else:
            return None


class EmailAuthenticationBackend(CustomAuthenticationBackend):
    """Allow users to log in using their e-mail address"""
    def custom_get_user(self, email):
        try:
            return User.objects.get(email=email)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None


class SSNAuthenticationBackend(CustomAuthenticationBackend):
    """Allow users to log in using their SSN"""
    def custom_get_user(self, ssn):
        # FIXME: This may be Iceland specific; we ignore dashes.
        ssn = ssn.replace('-', '').strip()

        try:
            return User.objects.get(userprofile__verified_ssn=ssn)
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            return None
