
from django.conf import settings
from django.shortcuts import render_to_response

from core.models import UserProfile


class UserSettingsMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):

        #check auto logout (https://stackoverflow.com/questions/14830669/how-to-expire-django-session-in-5minutes)
        if not request.user.is_authenticated() :
            #Can't log out if not logged in
            return

        try:
            if datetime.now() - request.session['last_touch'] > timedelta( 0, settings.AUTO_LOGOUT_DELAY * 60, 0):
                auth.logout(request)
                del request.session['last_touch']
                return
        except KeyError:
            pass

        request.session['last_touch'] = datetime.now()

        if not request.user.is_anonymous():
            # Make sure that the user is not only logged in, but verified
            profile = request.user.get_profile() # This should never fail, see login
            if not profile.kennitala and request.path_info != '/accounts/verify/' and request.path_info != '/accounts/logout/':
                ctx = { 'auth_url': settings.AUTH_URL }
                return render_to_response('registration/verification_needed.html', ctx)

