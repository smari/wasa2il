from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from core.models import UserProfile

from election.models import Election

from issue.models import Issue

from polity.forms import PolityForm
from polity.models import Polity


def polity_list(request):
    polities = Polity.objects.all()

    # Find user polities. Those are used to determine which voting issues,
    # open issues and elections are to be shown on the page as well.
    if request.user.is_authenticated():
        user_polities = request.user.polities.all()
    else:
        user_polities = Polity.objects.filter(is_nonmembers_readable=True)

    votingissues = Issue.objects.order_by("deadline_votes").filter(
        deadline_proposals__lt=datetime.now(),
        deadline_votes__gt=datetime.now(),
        polity__in=user_polities
    )
    openissues = Issue.objects.order_by("deadline_votes").filter(
        deadline_proposals__gt=datetime.now(),
        deadline_votes__gt=datetime.now(),
        polity__in=user_polities
    )
    elections = Election.objects.order_by("deadline_votes").filter(
        deadline_votes__gt=datetime.now(),
        polity__in=user_polities
    )

    ctx = {
        'polities': polities,
        'votingissues': votingissues,
        'openissues': openissues,
        'elections': elections,
    }
    return render(request, 'polity/polity_list.html', ctx)


def polity_view(request, polity_id):
    polity = get_object_or_404(Polity, id=polity_id)

    polity.update_agreements()

    ctx = {
        'polity': polity,
        'user': request.user,
        'user_is_member': polity.is_member(request.user),
        'politytopics': polity.topic_set.listing_info(request.user).all(),
        'agreements': polity.agreements(),
        'newissues': polity.issue_set.order_by('deadline_votes').filter(
            deadline_votes__gt=datetime.now() - timedelta(days=settings.RECENT_ISSUE_DAYS)
        ),
        'newelections': polity.election_set.filter(
            deadline_votes__gt=datetime.now() - timedelta(days=settings.RECENT_ELECTION_DAYS)
        ),
        'verified_user_count': polity.members.filter(userprofile__verified=True).count(),
        'settings': settings,
    }

    return render(request, 'polity/polity_detail.html', ctx)


@login_required
def polity_add_edit(request, polity_id=None):
    if not request.user.is_staff:
        raise PermissionDenied()

    if polity_id:
        polity = get_object_or_404(Polity, id=polity_id)
    else:
        polity = Polity()

    if request.method == 'POST':
        form = PolityForm(request.POST, instance=polity)
        if form.is_valid():
            polity = form.save()
            return redirect(reverse('polity', args=(polity.id,)))
    else:
        if polity.id:
            form = PolityForm(instance=polity)
        else:
            # Automatically set current user as an officer if we're starting
            # from scratch. Someone needs to take some responsibility here!
            form = PolityForm(instance=polity, initial={
                'officers': [request.user]
            })

    ctx = {
        'polity': polity,
        'form': form,
    }
    return render(request, 'polity/polity_form.html', ctx)
