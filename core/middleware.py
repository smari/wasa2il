
from django.conf import settings
from django.shortcuts import render_to_response

from core.models import UserProfile

from django.contrib import auth

from datetime import datetime, timedelta

class UserSettingsMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):

        if hasattr(settings, 'AUTO_LOGOUT_DELAY'):
            if not request.user.is_authenticated() :
                # Can't log out if not logged in
                return

            now = datetime.now()

            if 'last_visit' in request.session:
                last_visit = datetime.strptime(request.session['last_visit'], '%Y-%m-%d %H:%M:%S')
                if now - last_visit > timedelta(0, settings.AUTO_LOGOUT_DELAY * 60, 0):
                    auth.logout(request)
                    return

            request.session['last_visit'] = now.strftime('%Y-%m-%d %H:%M:%S')

        if hasattr(settings, 'SAML_1'): # Is SAML 1.2 support enabled?
            if not request.user.is_anonymous():
                # Make sure that the user is not only logged in, but verified
                profile = request.user.userprofile # This should never fail, see login
                if not profile.verified_ssn and request.path_info != '/accounts/verify/' and request.path_info != '/accounts/logout/':
                    ctx = { 'auth_url': settings.SAML_1['URL'] }
                    return render_to_response('registration/verification_needed.html', ctx)


