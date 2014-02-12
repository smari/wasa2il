
from django.conf import settings
from django.shortcuts import render_to_response

from core.models import UserProfile


class UserSettingsMiddleware(object):
    def __init__(self):
        pass

    def process_request(self, request):

        if not request.user.is_anonymous():
            # Make sure that the user is not only logged in, but verified
            profile = request.user.get_profile() # This should never fail, see login
            if not profile.kennitala and request.path_info != '/accounts/verify/' and request.path_info != '/accounts/logout/':
                ctx = { 'auth_url': settings.AUTH_URL }
                return render_to_response('registration/verification_needed.html', ctx)


        # Commented since profile is created on login now.
        # Delete this code if 2014-02-11 was a long time ago. -helgi@piratar.is
        #if request.user.is_authenticated():
        #    try:
        #        request.session['django_language'] = request.user.get_profile().language
        #    except (AttributeError, UserProfile.DoesNotExist):
        #        # pass
        #        pro = UserProfile()
        #        pro.user = request.user
        #        pro.language = settings.LANGUAGE_CODE
        #        pro.save()
        #        request.session['django_language'] = pro.language
        #else:
        #    request.session['django_language'] = "is"

