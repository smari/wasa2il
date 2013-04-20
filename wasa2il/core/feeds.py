from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import simplejson as json

from core.models import *
from core.forms import *
from core.json import jsonize, error

# TODO: Fix RSS.
def rssize(f):
    def wrapped(*args, **kwargs):
        m = f(*args, **kwargs)
        if isinstance(m, HttpResponse):
            return m
        return HttpResponse("<rss></rss>")

    return wrapped



@jsonize
def feed_json(request, polity, item):
    url = request.build_absolute_uri("/issue/")
    limit = int(request.REQUEST.get("limit", 10))
    offset = int(request.REQUEST.get("offset", 0))
    if limit > 200: limit = 200

    p = get_object_or_404(Polity, id=polity)
    if not p.is_nonmembers_readable and request.user not in p.members:
        return {"error": 403}

    if item == "issues":
        items = [{"id": x.id, "name": x.name, "url": url+"%d/" % x.id, "topics": [t.name for t in x.topics.all()], "description": x.description} for x in p.issue_set.all()[offset:(limit+offset)]]
        return items

@rssize
def feed_rss(request, polity, item):

    return {}
