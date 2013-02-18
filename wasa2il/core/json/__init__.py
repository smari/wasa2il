
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import settings

from core.models import Election
from core.models import ElectionVote
from core.models import Candidate
from core.models import Meeting
from core.models import MembershipRequest
from core.models import MembershipVote
from core.models import Polity
from core.models import Topic
from core.models import UserProfile
from core.models import UserTopic

from core.json.utils import jsonize, error
from core.json.document import *
from core.json.issue import *
from core.json.meeting import *


@jsonize
def user_exists(request):
	from hashlib import sha1
	ctx = {}
	username = request.REQUEST.get("username")
	signature = request.REQUEST.get("signature")
	m = sha1()
	m.update(":" + username + ":" + settings.SHARED_SECRET + ":")
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
	email = request.REQUEST.get("email", "")
	m = sha1()
	m.update(":" + username + ":" + password + ":" + settings.SHARED_SECRET + ":")
	if m.hexdigest() != signature:
		ctx["ok"] = False
		return ctx

	(user, created) = User.objects.get_or_create(username=username)
	user.is_active = True
	user.email = email
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
def election_poll(request):
	election = get_object_or_404(Election, id=request.REQUEST.get("election", 0))
	ctx = {}
	ctx["election"] = {}
	ctx["election"]["user_is_candidate"] = (request.user in [x.user for x in election.candidate_set.all()])
	ctx["election"]["is_voting"] = election.is_voting()
	ctx["election"]["votes"] = election.get_votes()
	ctx["election"]["candidates"] = election.get_candidates()
	context = {"election": election, "candidates": election.get_unchosen_candidates(request.user)}
	ctx["election"]["candidates"]["html"] = render_to_string("core/_election_candidate_list.html", context)
	ctx["election"]["vote"] = {}
	context = {"election": election, "candidates": election.get_vote(request.user)}
	ctx["election"]["vote"]["html"] = render_to_string("core/_election_candidate_list.html", context)
	ctx["ok"] = True
	return ctx


@login_required
@jsonize
def election_candidacy(request):
	election = get_object_or_404(Election, id=request.REQUEST.get("election", 0))
	if not request.user in election.polity.members.all():
		return election_poll(request)

	val = int(request.REQUEST.get("val", 0))
	if val == 0:
		Candidate.objects.filter(user=request.user, election=election).delete()
	else:
		cand, created = Candidate.objects.get_or_create(user=request.user, election=election)

	return election_poll(request)


@login_required
@jsonize
def election_vote(request):
	election = get_object_or_404(Election, id=request.REQUEST.get("election", 0))
	ctx = {}
	ctx["ok"] = True

	if not election.polity.is_member(request.user):
		ctx["ok"] = False
		return ctx

	order = request.REQUEST.getlist("order[]")

	ElectionVote.objects.filter(election=election, user=request.user).delete()

	for i in range(len(order)):
		candidate = Candidate.objects.get(id=order[i])
		vote = ElectionVote(election=election, user=request.user, candidate=candidate, value=i)
		vote.save()

	return election_poll(request)


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

