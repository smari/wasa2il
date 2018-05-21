
from django.conf import settings
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.urls import resolve

from core.models import UserProfile

from polity.models import Polity

from django.contrib import auth

from datetime import datetime, timedelta

# A middleware to make certain variables available to both templates and views.
class GlobalsMiddleware():
    def process_request(self, request):

        global_vars = {
            'polity': None,
            'user_is_member': False,
            'user_is_officer': False,
            'user_is_wrangler': False,
        }

        try:
            match = resolve(request.path)

            if 'polity_id' in match.kwargs:
                polity_id = int(match.kwargs['polity_id'])
                global_vars['polity'] = polity = Polity.objects.prefetch_related(
                    'members',
                    'officers',
                    'wranglers'
                ).get(id=polity_id)

                if not request.user.is_anonymous():
                    global_vars['user_is_member'] = request.user in polity.members.all()
                    global_vars['user_is_officer'] = request.user in polity.officers.all()
                    global_vars['user_is_wrangler'] = request.user in polity.wranglers.all()
        except:
            # Basically only 404-errors and such cause errors here. Besides,
            # we'll want to move on with our lives anyway.
            pass

        request.globals = global_vars


# Put this middleware before LocaleMiddleware to ignore HTTP_ACCEPT_LANGUAGE
# set by the browser and fall back to settings.LANGUAGE_CODE instead.
class IgnoreHTTPAcceptLanguageMiddleware(object):
    def process_request(self, request):
        if request.META.has_key('HTTP_ACCEPT_LANGUAGE'):
            del request.META['HTTP_ACCEPT_LANGUAGE']

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
                    return redirect('/accounts/logout?timeout=1')

            request.session['last_visit'] = now.strftime('%Y-%m-%d %H:%M:%S')

        if hasattr(settings, 'SAML_1'): # Is SAML 1.2 support enabled?
            if not request.user.is_anonymous():
                # Make sure that the user is not only logged in, but verified
                profile = request.user.userprofile # This should never fail, see login
                if (not profile.verified
                        and request.path_info != '/accounts/verify/'
                        and request.path_info != '/accounts/logout/'):
                    ctx = { 'auth_url': settings.SAML_1['URL'] }
                    return render_to_response('registration/verification_needed.html', ctx)
