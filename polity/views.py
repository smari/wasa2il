from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from core.models import UserProfile

from election.models import Election

from issue.models import Issue

from polity.forms import PolityForm
from polity.forms import PolityOfficersForm
from polity.models import Polity


def polity_list(request):
    polities = Polity.objects.all()

    issues_recent = Issue.objects.recent().filter(polity__in=polities).order_by('polity__name')
    elections_recent = Election.objects.recent().filter(polity__in=polities).order_by('polity__name')

    ctx = {
        'polities': polities,
        'issues_recent': issues_recent,
        'elections_recent': elections_recent,
        'RECENT_ISSUE_DAYS': settings.RECENT_ISSUE_DAYS,
        'RECENT_ELECTION_DAYS': settings.RECENT_ELECTION_DAYS,
    }
    return render(request, 'polity/polity_list.html', ctx)


def polity_view(request, polity_id):
    polity = get_object_or_404(Polity, id=polity_id)

    polity.update_agreements()

    sub_polities = polity.polity_set.all()

    ctx = {
        'sub_polities': sub_polities,
        'politytopics': polity.topic_set.listing_info(request.user).all(),
        'agreements': polity.agreements(),
        'issues_recent': polity.issue_set.recent(),
        'elections_recent': polity.election_set.recent(),
        'RECENT_ISSUE_DAYS': settings.RECENT_ISSUE_DAYS,
        'RECENT_ELECTION_DAYS': settings.RECENT_ELECTION_DAYS,
        'verified_user_count': polity.members.filter(userprofile__verified=True).count(),
    }

    return render(request, 'polity/polity_detail.html', ctx)


@login_required
def polity_add_edit(request, polity_id=None):
    if not request.user.is_staff and not request.globals['user_is_officer']:
        raise PermissionDenied()

    if polity_id:
        polity = get_object_or_404(Polity, id=polity_id)
    else:
        polity = Polity()

    if request.method == 'POST':
        form = PolityForm(request.POST, instance=polity)
        if form.is_valid():
            is_new = polity.id is None

            polity = form.save()

            # Make sure that the creator of the polity is also a member.
            if is_new:
                polity.members.add(request.user)
                polity.officers.add(request.user)

            return redirect(reverse('polity', args=(polity.id,)))
    else:
        form = PolityForm(instance=polity)

    ctx = {
        'polity': polity,
        'form': form,
    }
    return render(request, 'polity/polity_form.html', ctx)


@login_required
def polity_officers(request, polity_id):
    if not request.user.is_staff and not request.globals['user_is_officer']:
        raise PermissionDenied()

    polity = request.globals['polity']

    if request.method == 'POST':
        form = PolityOfficersForm(request.POST, instance=polity)
        if form.is_valid():
            polity = form.save()

            return redirect(reverse('polity', args=(polity.id,)))
    else:
        form = PolityOfficersForm(instance=polity)

    # Make only members from this polity available as officers.
    form.fields['officers'].queryset = polity.members.all()

    ctx = {
        'polity': polity,
        'form': form,
    }
    return render(request, 'polity/polity_officers_form.html', ctx)
