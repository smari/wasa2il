import random

from datetime import datetime
from datetime import timedelta
from hashlib import md5

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
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

from polity.models import Polity


def _ordered_candidates(user, all_candidates, candidates):
    # This will sort the unchosen candidates in a stable order which is
    # different for each individual user. Rather than make it completely
    # random, the list is alphabetical, but may or may not be reversed
    # and the starting point varies.
    if len(all_candidates) < 1:
        return []

    if user.is_authenticated:
        randish = int(md5((repr(user) + str(user.id)).encode('utf-8')).hexdigest()[:8], 16)
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

    user_can_vote = election.can_vote(request.user)
    all_candidates = election.get_candidates()

    ctx = {
        "logged_out": not request.user.is_authenticated,
        "election": {
            "user_is_candidate":
                (request.user in [x.user for x in election.candidate_set.all()]),
            "election_state": election.election_state(),
            "votes": election.get_vote_count(),
            "candidates": all_candidates,
            "vote": {}}}

    ctx["election"]["candidates"]["html"] = render_to_string(
        "election/_election_candidate_list.html", {
            "user_can_vote": user_can_vote,
            "election": election,
            "candidate_total": len(all_candidates),
            "candidates": _ordered_candidates(
                request.user,
                Candidate.objects.filter(election=election),
                election.get_unchosen_candidates(request.user)),
            "candidate_selected": False})

    ctx["election"]["vote"]["html"] = render_to_string(
        "election/_election_candidate_list.html", {
            "user_can_vote": user_can_vote,
            "election": election,
            "candidate_total": len(all_candidates),
            "candidates": election.get_vote(request.user),
            "candidate_selected": True})

    for k, v in kwargs.items():
        ctx["election"][k] = v

    ctx["ok"] = kwargs.get("ok", True)

    return ctx


@require_http_methods(["POST"])
@login_required
@jsonize
def election_candidacy(request):
    election = get_object_or_404(Election, id=request.POST.get("election", 0))
    if election.election_state() == 'concluded':
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

    logged_in = request.user.is_authenticated
    can_vote = logged_in and election.can_vote(request.user)
    if not (logged_in and can_vote and election.election_state() == 'voting'):
        ctx["please_login"] = not logged_in
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

    polity_id = int(request.GET.get('polity_id', 0))
    showclosed = int(request.GET.get('showclosed', 0)) # 0 = False, 1 = True

    try:
        if polity_id:
            elections = Election.objects.filter(polity_id=polity_id)
        else:
            elections = Election.objects.order_by('polity__name', '-deadline_votes')

        if not showclosed:
            elections = elections.recent()

        if polity_id:
            polity = get_object_or_404(Polity, id=polity_id)
        else:
            polity = None

        html_ctx = {
            'user': request.user,
            'polity': polity,
            'elections_recent': elections,
        }

        ctx['showclosed'] = showclosed
        ctx['html'] = render_to_string('election/_elections_recent_table.html', html_ctx)
        ctx['ok'] = True
    except Exception as e:
        ctx['error'] = e.__str__() if settings.DEBUG else 'Error raised. Turn on DEBUG for details.'

    return ctx


def election_stats_download(request, polity_id=None, election_id=None, filename=None):
    election = get_object_or_404(
        Election,
        id=election_id,
        polity_id=polity_id,
        is_processed=True,
        stats_publish_files=True
    )

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


@login_required
def election_candidates_details(request, polity_id, election_id):
    try:
        election = Election.objects.get(id=election_id, polity_id=polity_id, polity__officers=request.user)
    except Election.DoesNotExist:
        raise PermissionDenied()

    candidates = election.candidate_set.select_related('user__userprofile').order_by('user__userprofile__verified_name')

    candidate_list = ['"SSN","Name from registry","Email address","Username"']
    for user in [c.user for c in candidates]:
        candidate_list.append(','.join(['"%s"' % item for item in [
            user.userprofile.verified_ssn,
            user.userprofile.verified_name,
            user.email,
            user.username,
        ]]))

    filename = u'Candidates - %s.csv' % election.name

    response = HttpResponse('\n'.join(candidate_list), content_type='application/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    return response
