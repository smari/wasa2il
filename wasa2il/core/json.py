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
		m = f(*args, **kwargs)
		if isinstance(m, HttpResponse):
			return m
		return HttpResponse(json.dumps(m))

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

	try:
		ag = meeting.meetingagenda_set.all().order_by("order")[0]
		ag.done = 1
		ag.save()
	except:
		pass

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
		"agenda": [{"id": i.id, "item":i.item, "order":i.order, "done": i.done, "interventions": 
			[{"user": x.user.username, "order": x.order, "motion": x.motion, "done": x.done} 
			for x in i.meetingintervention_set.all()]} 
			for i in meeting.meetingagenda_set.all().order_by("order")],
	}
	ctx["ok"] = True
	
	return ctx


@login_required
@jsonize
def meeting_agenda_add(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not meeting.polity.is_member(request.user):
		ctx["ok"] = False
		return ctx	

	ag = MeetingAgenda()
	ag.meeting = meeting
	ag.item = request.REQUEST.get("item", "")
	try:
		ag.order = meeting.meetingagenda_set.all().order_by("-order")[0].order+1
	except:
		ag.order = 1

	ag.done = 0
	ag.save()

	return meeting_poll(request)

@login_required
@jsonize
def meeting_agenda_remove(request):
	ctx = {}


	agendaid = int(request.REQUEST.get('item', 0))
	if not agendaid:
		ctx["ok"] = False
		return ctx	
		
	agenda = get_object_or_404(MeetingAgenda, id=agendaid)

	if not agenda.meeting.id == int(request.REQUEST.get('meeting', 0)):
		ctx["ok"] = False
		return ctx

	if not agenda.meeting.polity.is_member(request.user):
		ctx["ok"] = False
		return ctx	

	agenda.delete()

	return meeting_poll(request)


@login_required
@jsonize
def meeting_agenda_reorder(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not meeting.polity.is_member(request.user):
		ctx["ok"] = False
		return ctx

	order = request.REQUEST.getlist("order[]");
	for i in range(len(order)):
		agendaitem = MeetingAgenda.objects.get(id=order[i])
		agendaitem.order = i
		agendaitem.save()

	return meeting_poll(request)


@login_required
@jsonize
def meeting_agenda_open(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not request.user in meeting.managers.all():
		ctx["ok"] = False
		return ctx

	meeting.is_agenda_open = True
	meeting.save()


@login_required
@jsonize
def meeting_agenda_close(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not request.user in meeting.managers.all():
		ctx["ok"] = False
		return ctx

	meeting.is_agenda_open = False
	meeting.save()


@login_required
@jsonize
def meeting_agenda_next(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not request.user in meeting.managers.all():
		ctx["ok"] = False
		return ctx

	lastag = meeting.meetingagenda_set.filter(done=1)
	for ag in lastag:
		ag.done = 2
		ag.save()

	try:
		nextag = meeting.meetingagenda_set.filter(done=0).order_by("order")[0]
		nextag.done = 1
		nextag.save()
	except:
		pass

	return meeting_poll(request)


@login_required
@jsonize
def meeting_agenda_prev(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not request.user in meeting.managers.all():
		ctx["ok"] = False
		return ctx

	lastag = meeting.meetingagenda_set.filter(done=1)
	for ag in lastag:
		ag.done = 0
		ag.save()

	try:
		nextag = meeting.meetingagenda_set.filter(done=2).order_by("-order")[0]
		nextag.done = 1
		nextag.save()
	except:
		pass

	return meeting_poll(request)


@login_required
@jsonize
def meeting_intervention_next(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not request.user in meeting.attendees.all():
		ctx["ok"] = False
		return ctx

	try:
		currentitem = meeting.meetingagenda_set.get(done=1)
	except:
		ctx["ok"] = False
		return ctx

	


	return meeting_poll(request)


@login_required
@jsonize
def meeting_intervention_prev(request):
	return meeting_poll(request)


@login_required
@jsonize
def meeting_intervention_add(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	meeting = get_object_or_404(Meeting, id=meetingid)

	if not request.user in meeting.attendees.all():
		ctx["ok"] = False
		return ctx

	motion = int(request.REQUEST.get('type', 0))
	if not motion:
		ctx["ok"] = False
		return ctx	

	try:
		currentitem = meeting.meetingagenda_set.get(done=1)
	except:
		ctx["ok"] = False
		return ctx

	intervention = MeetingIntervention()
	intervention.meeting = meeting
	intervention.user = request.user
	intervention.motion = motion
	intervention.agendaitem = currentitem
	intervention.done = 0

	if motion == 1:		# Request to speak
		try:
			lastspeak = MeetingIntervention.objects.filter(agendaitem=currentitem).order_by("-order")[0]
			if lastspeak.user == request.user:
				# TODO: Make this return an error, stating that you can't ask to talk twice in a row.
				return meeting_poll(request)
		except:
			pass
		try:
			intervention.order = MeetingIntervention.objects.filter(agendaitem=currentitem).order_by("-order")[0].order+1
		except:
			intervention.order = 1
	elif motion == 2:	# Request to reply directly
		try:
			lastspeak = MeetingIntervention.objects.filter(agendaitem=currentitem, motion__in=[2,3]).order_by("-order")[0]
			if lastspeak.user == request.user:
				# TODO: Make this return an error, stating that you can't ask to talk twice in a row.
				return meeting_poll(request)
		except:
			pass
		try:
			intervention.order = MeetingIntervention.objects.filter(agendaitem=currentitem, motion__in=[2,3]).order_by("-order")[0].order+1
		except:
			return meeting_poll(request)
	elif motion == 3:	# Request to clarify
		try:
			lastspeak = MeetingIntervention.objects.filter(agendaitem=currentitem, motion__in=[2,3]).order_by("-order")[0]
			if lastspeak.user == request.user:
				# TODO: Make this return an error, stating that you can't ask to talk twice in a row.
				return meeting_poll(request)
		except:
			pass
		try:
			intervention.order = MeetingIntervention.objects.filter(agendaitem=currentitem, motion__in=[2,3]).order_by("-order")[0].order+1
		except:
			return meeting_poll(request)
	elif motion == 4:	# Request to make a point of order
		try:
			lastspeak = MeetingIntervention.objects.filter(agendaitem=currentitem, motion__in=[2,3,4]).order_by("-order")[0]
			if lastspeak.user == request.user:
				# TODO: Make this return an error, stating that you can't ask to talk twice in a row.
				return meeting_poll(request)
		except:
			pass

		try:
			intervention.order = MeetingIntervention.objects.filter(agendaitem=currentitem, motion__in=[2,3,4]).order_by("-order")[0].order+1
		except:
			intervention.order = 1
	
	shift = MeetingIntervention.objects.filter(agendaitem=currentitem, order__gt=intervention.order)
	for i in shift:
		i.order += 1
		i.save()
		
	intervention.save()

	return meeting_poll(request)


@login_required
@jsonize
def topic_star(request):
	ctx = {}
	topicid = int(request.REQUEST.get('topic', 0))
	if not meetingid:
		ctx["ok"] = False
		return ctx	
		
	topic = get_object_or_404(Topic, id=topicid)

	ctx["topic"] = topic.id

	try:
		ut = UserTopic.objects.get(topic=topic, user=request.user)
		ut.delete()
		ctx["starred"] = False
	except:
		UserTopic(topic=topic, user=request.user).save()
		ctx["starred"] = True

	ctx["ok"] = True
	
	return ctx
