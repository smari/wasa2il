from datetime import datetime

from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from core.models import Polity

from election.forms import ElectionForm
from election.models import Election


@login_required
def election_add_edit(request, polity_id, election_id=None):
    try:
        polity = Polity.objects.get(id=polity_id, officers=request.user)
    except Polity.DoesNotExist:
        raise PermissionDenied()

    if election_id:
        election = get_object_or_404(Election, id=election_id, polity=polity)
    else:
        election = Election(polity=polity)

    if request.method == 'POST':
        form = ElectionForm(request.POST, instance=election)
        if form.is_valid():
            election = form.save()
            return redirect(reverse('election', args=(polity_id, election.id)))
    else:
        form = ElectionForm(instance=election)

    ctx = {
        'polity': polity,
        'election': election,
        'form': form,
    }
    return render(request, 'core/election_add_edit.html', ctx)


def election_view(request, polity_id, election_id):
    polity = get_object_or_404(Polity, id=polity_id)
    election = get_object_or_404(Election, polity=polity, id=election_id)

    voting_interface_enabled = election.is_voting and election.can_vote(request.user)

    if election.is_processed:
        ordered_candidates = election.get_winners()
        vote_count = election.result.vote_count
        statistics = election.get_stats(user=request.user)
        users = [c.user for c in ordered_candidates]
        if request.user in users:
            user_result = users.index(request.user) + 1
        else:
            user_result = None
    else:
        # Returning nothing! Some voting systems are too slow for us to
        # calculate results on the fly.
        ordered_candidates = []
        vote_count = election.get_vote_count
        statistics = None
        user_result = None

    ctx = {
        'polity': polity,
        'election': election,
        'step': request.GET.get('step', None),
        'now': datetime.now().strftime('%d/%m/%Y %H:%I'),
        'ordered_candidates': ordered_candidates,
        'statistics': statistics,
        'vote_count': vote_count,
        'voting_interface_enabled': voting_interface_enabled,
        'user_is_member': polity.is_member(request.user),
        'user_is_officer': polity.is_officer(request.user),
        'user_result': user_result,
        'can_vote': (request.user is not None and election.can_vote(request.user)),
        'can_run': (request.user is not None and election.can_be_candidate(request.user))
    }
    if voting_interface_enabled:
        ctx.update({
            'started_voting': election.has_voted(request.user),
            'finished_voting': False
        })
    return render(request, 'core/election_view.html', ctx)


def election_list(request, polity_id):
    polity = get_object_or_404(Polity, id=polity_id)

    elections = Election.objects.filter(
        polity=polity
    ).annotate(
        candidate_count=Count('candidate')
    ).order_by(
        '-deadline_votes'
    )

    ctx = {
        'polity': polity,
        'elections': elections,
    }
    return render(request, 'core/election_list.html', ctx)
