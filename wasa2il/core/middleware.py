from django.conf import settings

class UserSettingsMiddleware(object):
	def __init__(self):
		pass

	def process_request(self, request):
		if request.user.is_authenticated():
			request.session['django_language'] = request.user.get_profile().language

