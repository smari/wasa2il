from django.conf import settings
from core.models import *

class UserSettingsMiddleware(object):
	def __init__(self):
		pass

	def process_request(self, request):
		if request.user.is_authenticated():
			try:
				request.session['django_language'] = request.user.get_profile().language
			except:
				pro = UserProfile()
				pro.user = request.user
				pro.save()
				request.session['django_language'] = pro.language

