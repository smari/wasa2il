
from django.conf import settings
from django.shortcuts import render_to_response

from core.models import UserProfile

from django.contrib import auth

from datetime import datetime, timedelta

class UserSettingsMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):

        #check auto logout (https://stackoverflow.com/questions/14830669/how-to-expire-django-session-in-5minutes)
        if not request.user.is_authenticated() :
            #Can't log out if not logged in
            return

        now = datetime.now()

        if 'last_visit' in request.session:
            last_visit = datetime.strptime(request.session['last_visit'], '%Y-%m-%d %H:%M:%S')
            if now - last_visit > timedelta(0, settings.AUTO_LOGOUT_DELAY * 60, 0):
                auth.logout(request)
                return

        request.session['last_visit'] = now.strftime('%Y-%m-%d %H:%M:%S')

        if not request.user.is_anonymous():
            # Make sure that the user is not only logged in, but verified
            profile = request.user.get_profile() # This should never fail, see login
            if not profile.kennitala and request.path_info != '/accounts/verify/' and request.path_info != '/accounts/logout/':
                ctx = { 'auth_url': settings.AUTH_URL }
                return render_to_response('registration/verification_needed.html', ctx)


