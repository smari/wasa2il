from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import simplejson as json

from core.models import *
from core.forms import *

def jsonize(f):
        def wrapped(*args, **kwargs):
                return HttpResponse(json.dumps(f(*args, **kwargs)))

        return wrapped


@login_required
@jsonize
def document_statement_new(request, document, type):
	ctx = {}

	s = Statement()
	s.user = request.user
	s.document = get_object_or_404(Document, id=document)
	s.type = type

	if s.document.proposed:
		if s.user not in s.document.polity.members.all():
			return {"error": 403}
	else:
		if s.user != s.document.user:
			return {"error": 403}

	try:
		s.number = Statement.objects.get(document=s.document, type=s.type).order_by('-number')[0].number + 1
	except:
		s.number = 1

	s.save()

	so = StatementOption()

	so.text = request.REQUEST.get("text", "")
	so.user = request.user
	so.save()
	s.text.add(so)

	ctx["ok"] = True
	ctx["html"] = s.get_text()

	return ctx


@login_required
@jsonize
def document_statement_move(request, statement, order):
	return {}


@login_required
@jsonize
def document_statement_delete(request, statement):
	return {}


@login_required
@jsonize
def document_propose(request, document, state):
	ctx = {}

	document = get_object_or_404(Document, id=document)

	if request.user != document.user:
		return {"error": 403}

	ctx["ok"] = True	
	return ctx



