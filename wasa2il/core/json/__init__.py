from datetime import datetime

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings

from core.models import Election
from core.models import ElectionVote
from core.models import Candidate
from core.models import Polity
from core.models import Topic
from core.models import UserProfile
from core.models import UserTopic

from core.json.utils import jsonize, error


@jsonize
def election_poll(request):
    election = get_object_or_404(Election, id=request.REQUEST.get("election", 0))
    user_is_member = request.user in election.polity.members.all()
    ctx = {}
    ctx["election"] = {}
    ctx["election"]["user_is_candidate"] = (request.user in [x.user for x in election.candidate_set.all()])
    ctx["election"]["is_voting"] = election.is_voting()
    ctx["election"]["votes"] = election.get_votes()
    ctx["election"]["candidates"] = election.get_candidates()
    context = {"user_is_member": user_is_member, "election": election, "candidates": election.get_unchosen_candidates(request.user), "candidate_selected": False}
    ctx["election"]["candidates"]["html"] = render_to_string("core/_election_candidate_list.html", context)
    ctx["election"]["vote"] = {}
    context = {"user_is_member": user_is_member, "election": election, "candidates": election.get_vote(request.user), "candidate_selected": True}
    ctx["election"]["vote"]["html"] = render_to_string("core/_election_candidate_list.html", context)
    ctx["ok"] = True
    return ctx


@login_required
@jsonize
def election_candidacy(request):
    election = get_object_or_404(Election, id=request.REQUEST.get("election", 0))
    if election.is_closed() or not request.user in election.polity.members.all():
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

    if not election.polity.is_member(request.user) or election.is_closed():
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
    except UserTopic.DoesNotExist:
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


@jsonize
def election_showclosed(request):
    ctx = {}

    polity_id = int(request.REQUEST.get("polity_id")) # This should work.
    showclosed = int(request.REQUEST.get('showclosed', 0)) # 0 = False, 1 = True

    try:
        if showclosed == 1:
            elections = Election.objects.filter(polity_id=polity_id).order_by('-deadline_votes')
        else:
            elections = Election.objects.filter(polity_id=polity_id, deadline_votes__gt=datetime.now()).order_by('-deadline_votes')

        ctx['showclosed'] = showclosed
        ctx['html'] = render_to_string('core/_election_list_table.html', {'elections': elections })
        ctx['ok'] = True
    except Exception as e:
        ctx['error'] = e

    return ctx


@login_required
@jsonize
def get_polity_members(request, polity_id):
    ctx = {}

    polity = get_object_or_404(Polity, id=polity_id)
    ctx['members'] = [{'username': m.username, 'id': m.id, 'str': m.get_full_name() or str(m)} for m in polity.members.all()]
    ctx['ok'] = True

    return ctx


