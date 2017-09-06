import random

from datetime import datetime
from datetime import timedelta
from hashlib import md5

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.views.decorators.http import require_http_methods

from core.ajax.utils import jsonize

from election.models import Candidate
from election.models import Election
from election.models import ElectionVote


def _ordered_candidates(user, all_candidates, candidates):
    # This will sort the unchosen candidates in a stable order which is
    # different for each individual user. Rather than make it completely
    # random, the list is alphabetical, but may or may not be reversed
    # and the starting point varies.
    if len(all_candidates) < 1:
        return []

    if user.is_authenticated():
        randish = int(md5(repr(user) + str(user.id)).hexdigest()[:8], 16)
    else:
        randish = random.randint(0, 0xffffff)

    def _sname(u):
        try:
            return slugify(u.userprofile.displayname or u.username)
        except:
            return slugify(u.username)

    ordered = list(all_candidates)
    ordered.sort(key=lambda c: _sname(c.user))

    pivot = (randish // 4) % len(ordered)
    if randish % 2 == 0:
        ordered.reverse()
    part1 = ordered[pivot:]
    part2 = ordered[:pivot]

    return [c for c in (part1 + part2) if c in candidates]


@jsonize
def election_poll(request, **kwargs):
    election = get_object_or_404(Election,
        id=request.POST.get("election", request.GET.get("election", -1)))

    user_is_member = election.polity.is_member(request.user)
    user_can_vote = election.can_vote(request.user)
    all_candidates = election.get_candidates()

    ctx = {
        "logged_out": not request.user.is_authenticated(),
        "election": {
            "user_is_candidate":
                (request.user in [x.user for x in election.candidate_set.all()]),
            "is_voting": election.is_voting(),
            "is_waiting": election.is_waiting(),
            "is_closed": election.is_closed(),
            "votes": election.get_vote_count(),
            "candidates": all_candidates,
            "vote": {}}}

    ctx["election"]["candidates"]["html"] = render_to_string(
        "core/_election_candidate_list.html", {
            "user_is_member": user_is_member,
            "user_can_vote": user_can_vote,
            "election": election,
            "candidate_total": len(all_candidates),
            "candidates": _ordered_candidates(
                request.user,
                Candidate.objects.filter(election=election),
                election.get_unchosen_candidates(request.user)),
            "candidate_selected": False})

    ctx["election"]["vote"]["html"] = render_to_string(
        "core/_election_candidate_list.html", {
            "user_is_member": user_is_member,
            "user_can_vote": user_can_vote,
            "election": election,
            "candidate_total": len(all_candidates),
            "candidates": election.get_vote(request.user),
            "candidate_selected": True})

    for k, v in kwargs.iteritems():
        ctx["election"][k] = v

    ctx["ok"] = kwargs.get("ok", True)

    return ctx


@require_http_methods(["POST"])
@login_required
@jsonize
def election_candidacy(request):
    election = get_object_or_404(Election, id=request.POST.get("election", 0))
    if election.is_closed():
        return election_poll(request)

    val = int(request.POST.get("val", 0))
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


@require_http_methods(["POST"])
@login_required
@jsonize
def election_vote(request):
    election = get_object_or_404(Election, id=request.POST.get("election", -1))
    ctx = {}
    ctx["ok"] = True

    logged_in = request.user.is_authenticated()
    can_vote = logged_in and election.can_vote(request.user)
    is_voting = election.is_voting()
    is_closed = election.is_closed()
    if not (logged_in and can_vote and is_voting):
        ctx["please_login"] = not logged_in
        ctx["is_closed"] = is_closed
        ctx["can_vote"] = can_vote
        ctx["ok"] = False
        return ctx

    ok = True
    try:
        votes = request.POST.getlist("order[]")
        _record_votes(election, request.user, votes)
    except:
        # FIXME: Report with more granularity what went wrong.
        ok = False

    return election_poll(request, ok=ok)


@jsonize
def election_showclosed(request):
    ctx = {}

    polity_id = int(request.GET.get("polity_id")) # This should work.
    showclosed = int(request.GET.get('showclosed', 0)) # 0 = False, 1 = True

    try:
        if showclosed == 1:
            elections = Election.objects.filter(polity_id=polity_id).order_by('-deadline_votes')
        else:
            elections = Election.objects.filter(
                polity_id=polity_id,
                deadline_votes__gt=datetime.now() - timedelta(days=settings.RECENT_ELECTION_DAYS)
            ).order_by('-deadline_votes')

        ctx['showclosed'] = showclosed
        ctx['html'] = render_to_string('core/_election_list_table.html', {'elections': elections })
        ctx['ok'] = True
    except Exception as e:
        ctx['error'] = e

    return ctx


def election_ballots(request, pk=None):
    ctx = {}
    election = get_object_or_404(Election, pk=pk)
    if election.is_closed():
        ctx["ballotbox"] = election.get_ballots()
        return render_to_response("core/election_ballots.txt", ctx, context_instance=RequestContext(request), content_type="text/plain")
    else:
        raise PermissionDenied


def election_stats_download(request, polity_id=None, election_id=None, filename=None):
    election = get_object_or_404(Election, id=election_id, polity_id=polity_id)

    if not election.stats_publish_files:
        raise Http404

    filetype = filename.split('.')[-1].lower()
    assert(filetype in ('json', 'xlsx', 'ods', 'html'))

    response = HttpResponse(
        election.get_formatted_stats(filetype, user=request.user),
        content_type={
            'json': 'application/json; charset=utf-8',
            'ods': 'application/vnd.oasis.opendocument.spreadsheet',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'html': 'text/html; charset=utf-8'
        }.get(filetype, 'application/octet-stream'))

    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response
