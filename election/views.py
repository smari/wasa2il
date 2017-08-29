from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from core.models import Polity

from election.forms import ElectionForm
from election.models import Election


class ElectionCreateView(CreateView):
    model = Election
    context_object_name = "election"
    template_name = "core/election_form.html"
    form_class = ElectionForm
    success_url = "/polity/%(polity)d/election/%(id)d/"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        self.success_url = "/polity/" + str(self.polity.id) + "/election/$(id)d/"
        return super(ElectionCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(ElectionCreateView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.polity.is_member(self.request.user)
        return context_data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.polity = self.polity
        self.object.save()
        self.success_url = "/polity/" + str(self.polity.id) + "/election/" + str(self.object.id) + "/"
        return HttpResponseRedirect(self.get_success_url())


class ElectionDetailView(DetailView):
    model = Election
    context_object_name = "election"
    template_name = "core/election_detail.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        return super(ElectionDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        election = self.get_object()

        # Single variable for template to check which controls to enable
        voting_interface_enabled = (
            self.get_object().is_voting and
            self.get_object().can_vote(self.request.user))

        if election.is_processed:
            ordered_candidates = election.get_winners()
            vote_count = election.result.vote_count
            statistics = election.get_stats(user=self.request.user)
            users = [c.user for c in ordered_candidates]
            if self.request.user in users:
                user_result = users.index(self.request.user) + 1
            else:
                user_result = None
        else:
            # Returning nothing! Some voting systems are too slow for us to
            # calculate results on the fly.
            ordered_candidates = []
            vote_count = election.get_vote_count
            statistics = None
            user_result = None

        context_data = super(ElectionDetailView, self).get_context_data(*args, **kwargs)
        context_data.update(
            {
                'polity': self.polity,
                'step': self.request.GET.get('step', None),
                "now": datetime.now().strftime("%d/%m/%Y %H:%I"),
                'ordered_candidates': ordered_candidates,
                'statistics': statistics,
                'vote_count': vote_count,
                'voting_interface_enabled': voting_interface_enabled,
                'user_is_member': self.polity.is_member(self.request.user),
                'user_result': user_result,
                'facebook_title': '%s (%s)' % (election.name, self.polity.name),
                'can_vote': (self.request.user is not None and
                             self.object.can_vote(self.request.user)),
                'can_run': (self.request.user is not None and
                            self.object.can_be_candidate(self.request.user))
            }
        )
        if voting_interface_enabled:
            context_data.update({
                'started_voting': election.has_voted(self.request.user),
                'finished_voting': False
            })

        return context_data


class ElectionListView(ListView):
    model = Election
    context_object_name = "elections"
    template_name = "core/election_list.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        return super(ElectionListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):

        elections = Election.objects.filter(polity=self.polity).annotate(candidate_count=Count('candidate')).order_by('-deadline_votes')

        context_data = super(ElectionListView, self).get_context_data(*args, **kwargs)
        context_data.update({
            'polity': self.polity,
            'elections': elections,
        })

        return context_data
