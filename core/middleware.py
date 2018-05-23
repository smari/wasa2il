
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


# Middleware for automatically logging out a user once AUTO_LOGOUT_DELAY
# seconds have been reached without activity.
class AutoLogoutMiddleware():
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


# Middleware for requiring SAML verification before allowing a logged in user
# to do anything else.
class SamlMiddleware(object):
    def process_request(self, request):

        if hasattr(settings, 'SAML_1'): # Is SAML 1.2 support enabled?

            if hasattr(settings, 'SAML_VERIFICATION_EXCLUDE_URL_PREFIX_LIST'):
                exclude_urls = settings.SAML_VERIFICATION_EXCLUDE_URL_PREFIX_LIST
            else:
                exclude_urls = []

            # Short-hands.
            path_ok = request.path_info in [
                '/accounts/verify/',
                '/accounts/logout/',
                '/accounts/login-or-saml-redirect/'
            ] or any([request.path_info.find(p) == 0 for p in exclude_urls])
            logged_in = request.user.is_authenticated()
            verified = request.user.userprofile.verified if logged_in else False

            if logged_in and not verified and not path_ok:
                ctx = { 'auth_url': settings.SAML_1['URL'] }
                return render_to_response('registration/verification_needed.html', ctx)

    def process_response(self, request, response):

        if hasattr(settings, 'SAML_1'):
            logged_in = request.user.is_authenticated()
            verified = request.user.userprofile.verified if logged_in else False
            just_logged_in = (
                request.path == '/accounts/login/'
                and response.status_code == 302
                and response.url == settings.LOGIN_REDIRECT_URL
            )

            if logged_in and just_logged_in and not verified:
                return redirect('/accounts/login-or-saml-redirect/')

            return response
