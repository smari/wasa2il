
from django.http import HttpResponse
import json


def jsonize(f):
    def wrapped(*args, **kwargs):
        m = f(*args, **kwargs)
        if isinstance(m, HttpResponse):
            return m
        return HttpResponse(json.dumps(m), content_type='application/json')

    return wrapped


def error(msg, ctx={}):
    ctx['ok'] = False
    ctx['error'] = msg
    return ctx
