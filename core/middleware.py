
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
            'WASA2IL_VERSION': settings.WASA2IL_VERSION,
            'WASA2IL_HASH': settings.WASA2IL_HASH,
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


# Middleware for automatically logging out a user once AUTO_LOGOUT_DELAY
# seconds have been reached without activity.
class AutoLogoutMiddleware():
    def process_request(self, request):
        if hasattr(settings, 'AUTO_LOGOUT_DELAY'):

            now = datetime.now()

            if not request.user.is_authenticated() :
                # Set the last visit to now when attempting to log in, so that
                # auto-logout feature doesn't immediately log the user out
                # when the user is already logged out but the session is still
                # active.
                if request.path_info == '/accounts/login/' and request.method == 'POST':
                    request.session['last_visit'] = now.strftime('%Y-%m-%d %H:%M:%S')

                # Can't log out if not logged in
                return

            if 'last_visit' in request.session:
                last_visit = datetime.strptime(request.session['last_visit'], '%Y-%m-%d %H:%M:%S')
                if now - last_visit > timedelta(0, settings.AUTO_LOGOUT_DELAY * 60, 0):
                    auth.logout(request)
                    request.auto_logged_out = True

            request.session['last_visit'] = now.strftime('%Y-%m-%d %H:%M:%S')


# Middleware for requiring SAML verification before allowing a logged in user
# to do anything else.
class SamlMiddleware(object):
    def process_request(self, request):

        if settings.SAML_1['URL']: # Is SAML 1.2 support enabled?

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

        if settings.SAML_1['URL'] and hasattr(request, 'user'):
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
        return response


# This middleware is hopefully temporary. The vanilla
# TermsAndConditionsRedirectMiddleware currently does not support passing the
# URL's querystring onward. This means that an external service, using Django
# as an authentication mechanism, will not receive its token back from the
# login process if the terms and service need to be agreed to by the user.
# This custom replacement, which is hopefully temporary, is a self-contained
# and slightly refactored version of the vanilla
# TermsAndConditionsRedirectMiddleware from django-termsandconditions version
# 1.2.8.
#
# The fix we needed is adding the querystring in the "for term in
# TermsAndConditions..." loop. The same change has already been proposed as a
# pull request to its author:
#     https://github.com/cyface/django-termsandconditions/pull/75
#
# TODO: Once the problem has been fixed in the official version of
# django-termsandconditions, this entire class and its preceding import lines
# should be removed, its mention in settings.py should be set to the official
# package's edition. No further changes should be necessary to deprecate it.
from termsandconditions.models import TermsAndConditions
from termsandconditions.pipeline import redirect_to_terms_accept
class CustomTermsAndConditionsRedirectMiddleware():
    """
    This middleware checks to see if the user is logged in, and if so,
    if they have accepted all the active terms.
    """

    def process_request(self, request):
        """Process each request to app to ensure terms have been accepted"""

        current_path = request.META['PATH_INFO']

        user_authenticated = request.user.is_authenticated()

        if user_authenticated and self.is_path_protected(current_path):
            for term in TermsAndConditions.get_active_terms_not_agreed_to(request.user):
                # Check for querystring and include it if there is one
                qs = request.META['QUERY_STRING']
                current_path += '?' + qs if qs else ''
                return redirect_to_terms_accept(current_path, term.slug)

        return None

    def is_path_protected(self, path):
        """
        returns True if given path is to be protected, otherwise False

        The path is not to be protected when it appears on:
        TERMS_EXCLUDE_URL_PREFIX_LIST, TERMS_EXCLUDE_URL_LIST or as
        ACCEPT_TERMS_PATH
        """
        protected = True

        ACCEPT_TERMS_PATH = getattr(
            settings,
            'ACCEPT_TERMS_PATH',
            '/terms/accept/'
        )

        TERMS_EXCLUDE_URL_PREFIX_LIST = getattr(
            settings,
            'TERMS_EXCLUDE_URL_PREFIX_LIST',
            {'/admin', '/terms'}
        )

        TERMS_EXCLUDE_URL_LIST = getattr(
            settings,
            'TERMS_EXCLUDE_URL_LIST',
            {'/', '/termsrequired/', '/logout/', '/securetoo/'}
        )

        for exclude_path in TERMS_EXCLUDE_URL_PREFIX_LIST:
            if path.startswith(exclude_path):
                protected = False

        if path in TERMS_EXCLUDE_URL_LIST:
            protected = False

        if path.startswith(ACCEPT_TERMS_PATH):
            protected = False

        return protected
