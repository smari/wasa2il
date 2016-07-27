from datetime import datetime
from hashlib import md5

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.db.models import Q
from django.db import transaction
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

from core.ajax.utils import jsonize, error


def _ordered_candidates(user, all_candidates, candidates):
    # This will sort the unchosen candidates in a stable order which is
    # different for each individual user. Rather than make it completely
    # random, the list is alphabetical, but may or may not be reversed
    # and the starting point varies.
    if len(all_candidates) < 1:
        return []

    randish = int(md5(repr(user) + str(user.id)).hexdigest()[:8], 16)

    ordered = list(all_candidates)
    ordered.sort(key=lambda k: unicode(k).lower())

    pivot = (randish // 2) % len(ordered)
    part1 = ordered[pivot:]
    part2 = ordered[:pivot]
    if randish % 4 in (0, 2):
        part1.reverse()
    if randish % 4 in (1, 2):
        part2.reverse()

    return [c for c in (part1 + part2) if c in candidates]


@jsonize
def election_poll(request, **kwargs):
    election = get_object_or_404(Election, id=request.GET.get("election", 0))
    user_is_member = election.polity.is_member(request.user)
    user_can_vote = election.can_vote(request.user)
    all_candidates = election.get_candidates()
    ctx = {}
    ctx["election"] = {}
    ctx["election"]["user_is_candidate"] = (request.user in [x.user for x in election.candidate_set.all()])
    ctx["election"]["is_voting"] = election.is_voting()
    ctx["election"]["is_waiting"] = election.is_waiting()
    ctx["election"]["is_closed"] = election.is_closed()
    ctx["election"]["votes"] = election.get_vote_count()
    ctx["election"]["candidates"] = all_candidates
    ctx["election"]["candidates"]["html"] = render_to_string(
        "core/_election_candidate_list.html", {
            "user_is_member": user_is_member,
            "user_can_vote": user_can_vote,
            "election": election,
            "candidates": _ordered_candidates(
                request.user,
                Candidate.objects.filter(election=election),
                election.get_unchosen_candidates(request.user)),
            "candidate_selected": False})
    ctx["election"]["vote"] = {}
    ctx["election"]["vote"]["html"] = render_to_string(
        "core/_election_candidate_list.html", {
            "user_is_member": user_is_member,
            "user_can_vote": user_can_vote,
            "election": election,
            "candidates": election.get_vote(request.user),
            "candidate_selected": True})

    for k, v in kwargs:
        ctx["election"][k] = v

    ctx["ok"] = kwargs.get("ok", True)

    return ctx


@login_required
@jsonize
def election_candidacy(request):
    election = get_object_or_404(Election, id=request.GET.get("election", 0))
    if election.is_closed():
        return election_poll(request)

    val = int(request.GET.get("val", 0))
    if val == 0:
        Candidate.objects.filter(user=request.user, election=election).delete()
    elif election.can_be_candidate(request.user):
        cand, created = Candidate.objects.get_or_create(user=request.user, election=election)

    return election_poll(request)


@transaction.atomic
def _record_votes(election, user, order):
    ElectionVote.objects.filter(election=election, user=user).delete()

    for i in range(len(order)):
        candidate = Candidate.objects.get(id=order[i])
        ElectionVote(
            election=election, user=user, candidate=candidate, value=i
            ).save()


@login_required
@jsonize
def election_vote(request):
    election = get_object_or_404(Election, id=request.GET.get("election", 0))
    ctx = {}
    ctx["ok"] = True

    if not election.can_vote(request.user) or election.is_closed():
        ctx["ok"] = False
        return ctx

    ok = True
    try:
        _record_votes(election, request.user, request.GET.getlist("order[]"))
    except:
        # FIXME: Report with more granularity what went wrong.
        ok = False

    return election_poll(request, ok=ok)


@login_required
@jsonize
def topic_star(request):
    ctx = {}
    topicid = int(request.GET.get('topic', 0))
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
    profile = UserProfile.objects.get(user=request.user)
    profile.topics_showall = not profile.topics_showall
    profile.save()

    ctx["showstarred"] = not profile.topics_showall

    polity = int(request.GET.get("polity", 0))
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

    polity_id = int(request.GET.get("polity_id")) # This should work.
    showclosed = int(request.GET.get('showclosed', 0)) # 0 = False, 1 = True

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


