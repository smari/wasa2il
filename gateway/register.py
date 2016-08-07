import hashlib
import time

from django.conf import settings
from django.contrib.auth import logout
from registration.backends.simple.views import RegistrationView


class PreverifiedRegistrationView(RegistrationView):
    """
    A registration backend which accepts e-mail addresses which have been
    validated by icepirate and immediately creates a user.
    """
    SIG_VALIDITY = 31 * 24 * 3600

    def _make_email_sig(self, email, when=None):
        ts = '%x/' % (when or time.time())
        key = settings.ICEPIRATE['key']
        return ts + hashlib.sha1(
            '%s:%s%s:%s' % (key, ts, email, key)).hexdigest()

    def _email_sig_is_ok(self, email, email_sig):
        try:
            ts, sig = email_sig.split('/')
            ts = int(ts, 16)
            if time.time() - ts > self.SIG_VALIDITY:
                return False
            return email_sig == self._make_email_sig(email, when=ts)
        except (AttributeError, ValueError, IndexError, KeyError):
            return False

    def registration_allowed(self):
        # Check if there is an email_sig variable that correctly signs
        # the provided e-mail address. 

        email = self.request.GET.get('email')
        email2 = self.request.POST.get('email')
        email_sig = self.request.GET.get('email_sig')

        if email2 is None and email_sig is None:
            return True
        elif (email2 in (None, email)
                and self._email_sig_is_ok(email, email_sig)):
            return RegistrationView.registration_allowed(self)
        else:
            return False

    def register(self, form):
        new_user = RegistrationView.register(self, form)
        logout(self.request)
        return new_user

    def get_success_url(self, user=None):
        return 'registration_activation_complete'
