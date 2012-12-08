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
def polity_membershipvote(request):
	ctx = {}
	try:
		id = int(request.POST.get('id'))
	except ValueError:
		id = None
	validator = request.user
	mrequest = MembershipRequest.objects.get(id=id, polity__members=validator)
	vote, created = MembershipVote.objects.get_or_create(voter=request.user, user=mrequest.requestor, polity=mrequest.polity)

	ctx["accepted"] = mrequest.get_fulfilled()
	ctx["percent"] = mrequest.votespercent()
	ctx["votes"] = mrequest.votes()
	ctx["votesneeded"] = mrequest.votesneeded()
	ctx["username"] = mrequest.requestor.username
	ctx["ok"] = True

	return ctx


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


@login_required
@jsonize
def meeting_start(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	meeting.time_started = datetime.now()
	meeting.save()

	return ctx


@login_required
@jsonize
def meeting_end(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	meeting.time_ended = datetime.now()
	meeting.save()

	return ctx



@login_required
@jsonize
def meeting_attend(request, meeting):
	ctx = {}

	meeting = get_object_or_404(Meeting, id=meeting)

	if not meeting.polity.is_member(request.user):
		ctx["ok"] = False
		return ctx	

	meeting.attendees.add(request.user)
	ctx["ok"] = True
	return ctx


@login_required
@jsonize
def meeting_poll(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not meeting.polity.is_member(request.user):
		ctx["ok"] = False
		return ctx	

	try:	time_starts = meeting.time_starts.strftime("%d/%m/%Y %H:%I")
	except:	time_starts = None
	try:	time_started = meeting.time_started.strftime("%d/%m/%Y %H:%I")
	except:	time_started = None
	try:	time_ends = meeting.time_ends.strftime("%d/%m/%Y %H:%I")
	except:	time_ends = None
	try:	time_ended = meeting.time_ended.strftime("%d/%m/%Y %H:%I")
	except:	time_ended = None


	ctx["polity"] = {"name": meeting.polity.name}
	ctx["meeting"] = {
		"called_by": meeting.user.username, 
		"time_starts": time_starts,
		"time_starts_iso": str(meeting.time_starts),
		"time_started": time_started,
		"time_started_iso": str(meeting.time_started),
		"time_ends": time_ends,
		"time_ends_iso": str(meeting.time_ends),
		"time_ended": time_ended,
		"time_ended_iso": str(meeting.time_ended),
		"is_agenda_open": meeting.is_agenda_open,
		"is_not_started": meeting.notstarted(),
		"is_ongoing": meeting.ongoing(),
		"is_ended": meeting.ended(),
		"managers": [user.username for user in meeting.managers.all()],
		"attendees": [user.username for user in meeting.attendees.all()],
		"user_is_manager": request.user in meeting.managers.all(),
		"user_is_attendee": request.user in meeting.attendees.all(),
	}
	ctx["ok"] = True
	
	return ctx
