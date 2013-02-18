
from django.http import HttpResponse
import simplejson as json


def jsonize(f):
	def wrapped(*args, **kwargs):
		m = f(*args, **kwargs)
		if isinstance(m, HttpResponse):
			return m
		return HttpResponse(json.dumps(m))

	return wrapped


def error(msg, ctx={}):
	ctx['ok'] = False
	ctx['error'] = msg
	return ctx
