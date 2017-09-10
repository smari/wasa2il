from datetime import datetime
from datetime import timedelta

from django.conf import settings
from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView

from election.models import Election

from issue.models import Issue

from polity.forms import PolityForm
from polity.models import Polity


class PolityListView(ListView):
    model = Polity
    context_object_name = 'polities'
    template_name = 'polity/polity_list.html'

    def get_context_data(self, *args, **kwargs):
        ctx = {}
        context_data = super(PolityListView, self).get_context_data(*args, **kwargs)

        if self.request.user.is_authenticated():
            polities = self.request.user.polities.all()
        else:
            polities = Polity.objects.filter(is_nonmembers_readable=True)

        ctx["votingissues"] = Issue.objects.order_by("deadline_votes").filter(deadline_proposals__lt=datetime.now(),deadline_votes__gt=datetime.now(),polity__in=polities)
        ctx["openissues"] = Issue.objects.order_by("deadline_votes").filter(deadline_proposals__gt=datetime.now(),deadline_votes__gt=datetime.now(),polity__in=polities)
        ctx["elections"] = Election.objects.order_by("deadline_votes").filter(deadline_votes__gt=datetime.now(),polity__in=polities)

        context_data.update(ctx)
        return context_data

class PolityDetailView(DetailView):
    queryset = Polity.objects.prefetch_related('officers')
    context_object_name = "polity"
    template_name = 'polity/polity_detail.html'

    def dispatch(self, *args, **kwargs):
        res = super(PolityDetailView, self).dispatch(*args, **kwargs)
        return res

    def get_context_data(self, *args, **kwargs):
        ctx = {}
        context_data = super(PolityDetailView, self).get_context_data(*args, **kwargs)
        self.object.update_agreements()
        ctx['user_is_member'] = self.object.is_member(self.request.user)
        ctx["politytopics"] = self.object.topic_set.listing_info(self.request.user).all()
        ctx["agreements"] = self.object.agreements()
        ctx["newissues"] = self.object.issue_set.order_by("deadline_votes").filter(
            deadline_votes__gt=datetime.now() - timedelta(days=settings.RECENT_ISSUE_DAYS)
        )
        ctx["newelections"] = self.object.election_set.filter(
            deadline_votes__gt=datetime.now() - timedelta(days=settings.RECENT_ELECTION_DAYS)
        )
        ctx["settings"] = settings

        context_data.update(ctx)
        return context_data


class PolityCreateView(CreateView):
    model = Polity
    context_object_name = "polity"
    template_name = "polity/polity_form.html"
    form_class = PolityForm
    success_url = "/polity/%(id)d/"

    def form_valid(self, form):
        self.object = form.save()
        self.object.members.add(self.request.user)
        return super(PolityCreateView, self).form_valid(form)
