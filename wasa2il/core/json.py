
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timesince import timesince
import simplejson as json
import settings

from core.models import *
from core.forms import *


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


@jsonize
def user_exists(request):
	from hashlib import sha1
	ctx = {}
	username = request.REQUEST.get("username")
	signature = request.REQUEST.get("signature")
	m = sha1()
	m.update(":"+username+":"+settings.SHARED_SECRET+":")
	if m.hexdigest() != signature:
		ctx["ok"] = False
		return ctx

	try:
		User.objects.get(username=username)
		ctx["user_exists"] = True
	except:
		ctx["user_exists"] = False
	
	ctx["ok"] = True
	return ctx


@jsonize
def user_create(request):
	from hashlib import sha1

	ctx = {}
	username = request.REQUEST.get("username")
	password = request.REQUEST.get("password")
	signature = request.REQUEST.get("signature")
	m = sha1()
	m.update(":"+username+":"+password+":"+settings.SHARED_SECRET+":")
	if m.hexdigest() != signature:
		ctx["ok"] = False
		return ctx

	(user, created) = User.objects.get_or_create(username=username)
	user.is_active = True
	user.set_password(password)
	user.save()
	pro = UserProfile()
	pro.user = user
	pro.save()

	ctx["ok"] = True
	ctx["username"] = user.username
	ctx["id"] = user.id
	return ctx


@login_required
@jsonize
def issue_vote(request):
	ctx = {}
	issue = int(request.REQUEST.get("issue", 0))
	issue = get_object_or_404(Issue, id=issue)

	if not issue.is_voting():
		return issue_poll(request)

	if not request.user in issue.polity.members:
		return issue_poll(request)

	val = int(request.REQUEST.get("vote", 0))

	(vote, created) = Vote.objects.get_or_create(user=request.user, issue=issue)
	vote.value = val
	vote.save()

	return issue_poll(request)


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

	ctx["accepted"] = mrequest.fulfilled
	ctx["percent"] = mrequest.votespercent()
	ctx["votes"] = mrequest.votes()
	ctx["votesneeded"] = mrequest.votesneeded()
	ctx["username"] = mrequest.requestor.username
	ctx["ok"] = True

	return ctx


@login_required
@jsonize
def issue_document_import(request):
	ctx = {"ok": True}

	issue = get_object_or_404(Issue, id=request.REQUEST.get("issue"))
	doc = get_object_or_404(Document, id=request.REQUEST.get("document"))

	if not doc.polity == issue.polity:
		return {"ok": False}

	if not doc.is_adopted:
		return {"ok": False}

	doc.issues.add(issue)

	return ctx



@login_required
@jsonize
def document_changeproposal_new(request, document, type):
	ctx = {}

	doc = get_object_or_404(Document, id=document)

	if doc.is_proposed:
		return document_statement_new(request, document, type)

	if request.user not in doc.polity.users.all():
		ctx['error'] = 403
		return ctx

	s = ChangeProposal()
	s.user = request.user
	s.document = doc
	s.contenttype = type
	s.actiontype = 4
	# s.refitem = 
	# s.destination =
	# s.content =

	return ctx


@login_required
@jsonize
def document_statements_import(request):
	ctx = {}
	ctx["list"] = []

	doc = get_object_or_404(Document, id=request.GET.get("document"))
	text = request.GET.get("text", "")
	lines = text.split("\n")

	if request.user != doc.user:
		return {"error": 403}

	for line in lines:
		s = Statement()
		s.user = request.user
		s.document = doc
		s.text = line[1:].strip()

		if len(line) == 0:
			continue

		if line[0] == "\#":
			# Subheading
			s.type = 3
		elif line[0] == "-":
			# Reference
			s.type = 0
		elif line[0] == ":":
			# Assumption
			s.type = 1
		elif line[0] == "*":
			# Statement
			s.type = 2
		else:
			continue

		try:
			s.number = Statement.objects.get(document=s.document, type=s.type).order_by('-number')[0].number + 1
		except:
			s.number = 1

		s.save()

		boom = {}
		boom["id"] = s.id
		boom["seq"] = s.number
		boom["html"] = str(s)
		ctx["list"].append(boom)

	return ctx


@login_required
@jsonize
def document_statement_new(request, document, type):
	ctx = {}

	doc = get_object_or_404(Document, id=document)

	if doc.is_proposed:
		return document_changeproposal_new(request, document, type)

	s = Statement()
	s.user = request.user
	s.document = doc
	s.type = type
	s.text = request.GET.get('text', '')

	if s.user != s.document.user:
		return {"error": 403}

	try:
		s.number = Statement.objects.get(document=s.document, type=s.type).order_by('-number')[0].number + 1
	except:
		s.number = 1

	s.save()

	ctx["ok"] = True
	ctx["id"] = s.id
	ctx["seq"] = s.number
	ctx["html"] = str(s)

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

	ctx["state"] = bool(int(state))
	document.is_proposed = bool(int(state))
	document.save()

	issue_id = int(request.REQUEST.get("issue", 0))
	if issue_id:
		issue = Issue.objects.get(id=issue_id)
		ctx["html_user_documents"] = render_to_string("core/_document_proposals_list_table.html", {"documents": issue.user_documents(request.user)})
		ctx["html_all_documents"] = render_to_string("core/_document_list_table.html", {"documents": issue.proposed_documents()})


	ctx["ok"] = True	
	return ctx


@login_required
@jsonize
def issue_comment_send(request):
	issue = get_object_or_404(Issue, id=request.REQUEST.get("issue", 0))
	text = request.REQUEST.get("comment")
	comment = Comment()
	comment.created_by = request.user
	comment.comment = text
	comment.issue = issue
	comment.save()
	return issue_poll(request)


@login_required
@jsonize
def issue_poll(request):
	issue = get_object_or_404(Issue, id=request.REQUEST.get("issue", 0))
	ctx = {}
	comments = [{"id": comment.id, "created_by": comment.created_by.username, "created": str(comment.created), "created_since": timesince(comment.created), "comment": comment.comment} for comment in issue.comment_set.all().order_by("created")]
	documents = []
	ctx["issue"] = {"comments": comments, "documents": documents}
	ctx["ok"] = True
	ctx["issue"]["votes"] = issue.get_votes()
	try:
		v = Vote.objects.get(user=request.user, issue=issue)
		ctx["issue"]["vote"] = v.get_value()
	except: pass
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
		"managers": [{'username': user.username, 'id': user.id, 'str': user.get_full_name() or str(user)} for user in meeting.managers.all()],
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
		ag.order = meeting.meetingagenda_set.all().order_by("-order")[0].order + 1
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

	order = request.REQUEST.getlist("order[]")
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

	return ctx


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

	return ctx


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
	intervention.order = 1

	try:
		last_speaker = MeetingIntervention.objects.filter(agendaitem=currentitem).order_by('-order')[0]
	except IndexError:
		last_speaker = None
		if motion != MOTION['TALK']:
			return error('The first intervention must be a talk (FOR NOW)', ctx)
	else:

		same = last_speaker.user == request.user
		intervention.order = last_speaker.order + 1

		if motion == MOTION['TALK']:           # Request to talk

			if same and last_speaker.motion == MOTION['TALK']:
				return error('One cannot TALK twice in a row.')

		if motion == MOTION['REPLY']:           # Request to reply directly

			if same and last_speaker.motion in (MOTION['TALK'], MOTION['REPLY']):
				return error('One cannot REPLY to own\'s REPLY.')

			if last_speaker.motion not in (MOTION['TALK'], MOTION['REPLY'], ):
				return error('One can only REPLY to a TALK or another REPLY', ctx)

		elif motion == MOTION['CLARIFY']:		# Request to clarify

			raise NotImplementedError('This is not implemented now. TALK and REPLY should be enough for now.')

		elif motion == MOTION['POINT']:		    # Request to make a point of order

			raise NotImplementedError('This is not implemented now. TALK and REPLY should be enough for now.')

	# Shift all existing interventions with greater-or-equal order
	for i in MeetingIntervention.objects.filter(agendaitem=currentitem, order__gte=intervention.order):
		i.order += 1
		i.save()

	# Finally save the new intervention
	intervention.save()

	return meeting_poll(request)


@login_required
@jsonize
def meeting_manager_add(request):
	ctx = {}

	meetingid = int(request.REQUEST.get('meeting', 0))
	if not meetingid:
		ctx["ok"] = False
		ctx['error'] = 'Meeting not found'
		return ctx

	meeting = get_object_or_404(Meeting, id=meetingid)

	if not request.user in meeting.managers.all():
		ctx["ok"] = False
		ctx['error'] = 'You are not a manger!'
		return ctx

	uq = request.REQUEST.get("user", "")
	try:
		u = User.objects.get(Q(username__iexact=uq) | Q(first_name__iexact=uq) | Q(last_name__iexact=uq))
		print u
	except User.DoesNotExist:
		ctx["ok"] = False
		ctx['error'] = 'User "%s" not found' % uq
		return ctx
	except User.MultipleObjectsReturned:
		ctx["ok"] = False
		ctx['error'] = 'Too many users found for query: %s' % uq
		return ctx

	if u in meeting.managers.all():
		ctx["ok"] = False
		ctx['error'] = 'User already a manger!'
		return ctx

	meeting.managers.add(u)

	return meeting_poll(request)


@login_required
@jsonize
def topic_star(request):
	ctx = {}
	topicid = int(request.REQUEST.get('topic', 0))
	if not topicid:
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

	topics = topic.polity.get_topic_list(request.user)
	ctx["html"] = render_to_string("core/_topic_list_table.html", {"topics": topics, "user": request.user, "polity": topic.polity})

	ctx["ok"] = True

	return ctx


@login_required
@jsonize
def topic_showstarred(request):
	ctx = {}
	profile = request.user.get_profile()
	profile.topics_showall = not profile.topics_showall
	profile.save()

	ctx["showstarred"] = not profile.topics_showall

	polity = int(request.REQUEST.get("polity", 0))
	if polity:
		try:
			polity = Polity.objects.get(id=polity)
			topics = polity.get_topic_list(request.user)
			ctx["html"] = render_to_string("core/_topic_list_table.html", {"topics": topics, "user": request.user, "polity": polity})
		except Exception, e:
			ctx["error"] = e

	ctx["ok"] = True
	return ctx


@login_required
@jsonize
def get_polity_members(request, polity_id):
	ctx = {}

	polity = get_object_or_404(Polity, id=polity_id)
	ctx['members'] = [{'username': m.username, 'id': m.id, 'str': m.get_full_name() or str(m)} for m in polity.members.all()]
	ctx['ok'] = True

	return ctx


@login_required
@jsonize
def list_attendees(request, meeting_id):
	'''
	List attendees for a specific meeting.
	Requesting user must be an admin in the meeting.
	Supplying a 'filter' GET parameter to filter the results by name/username.
	'''
	ctx = {}

	try:
		meeting_id = int(meeting_id)
	except ValueError:
		return error('Invalid parameter (meeting_id). Should be a positive integer.')

	try:
		meeting = Meeting.objects.get(id=meeting_id)
	except Meeting.DoesNotExist:
		return error('Meeting object not found')

	try:
		meeting.managers.get(id=request.user.id)
	except User.DoesNotExist:
		return error('You must be a meeting manager to list the attendees.')

	filter_term = request.GET.get('filter', None)

	limit = 10
	qs = (
		Q(first_name__istartswith=filter_term) |
		Q(last_name__istartswith=filter_term) |
		Q(username__istartswith=filter_term)
	)
	attendees = meeting.attendees.filter(qs)[:limit]

	# TODO: Why will the below not work? Later...
	#qs = (
	#>	Q(first_name__icontains=filter_term) |
	#	Q(last_name__icontains=filter_term) |
	#	Q(username__icontains=filter_term) 
	#)
	#attendees = meeting.attendees.filter(qs, id__not=[a.id for a in attendees])[:limit - len(attendees)]

	ctx['attendees'] = [
		{
			'id': m.id,
			'username': m.username,
			'str': m.get_full_name() or str(m),
		} for m in attendees
	]
	ctx['ok'] = True

	return ctx
