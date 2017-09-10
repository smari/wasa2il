import json

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView

from core.models import DocumentContent

from issue.forms import IssueForm
from issue.models import Issue

from polity.models import Polity

from topic.models import Topic


class IssueCreateView(CreateView):
    context_object_name = "issue"
    template_name = "issue/issue_form.html"
    form_class = IssueForm
    success_url = "/issue/%(id)d/"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])

        if self.polity.is_newissue_only_officers and self.request.user not in self.polity.officers.all():
            raise PermissionDenied()

        return super(IssueCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(IssueCreateView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.polity.is_member(self.request.user)
        context_data['form'].fields['topics'].queryset = Topic.objects.filter(polity=self.polity)
        context_data['selected_topics'] = []

        selected_topics = []
        if self.kwargs['documentcontent']:
            current_content = DocumentContent.objects.get(id=self.kwargs['documentcontent'])

            if current_content.order > 1:
                previous_topics = current_content.previous_topics()
                context_data['selected_topics'] = json.dumps(previous_topics)
                context_data['tab'] = 'diff'

            context_data['documentcontent'] = current_content
            context_data['documentcontent_comments'] = current_content.comments.replace("\n", "\\n")
            context_data['selected_diff_documentcontent'] = current_content.document.preferred_version()

        return context_data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.polity = self.polity

        self.object.apply_ruleset()

        context_data = self.get_context_data(form=form)
        if 'documentcontent' in context_data:
            self.object.documentcontent = context_data['documentcontent']

        self.object.save()

        for topic in form.cleaned_data.get('topics'):
            self.object.topics.add(topic)

        return HttpResponseRedirect(self.get_success_url())


class IssueDetailView(DetailView):
    model = Issue
    context_object_name = "issue"
    template_name = "issue/issue_detail.html"

    def get_context_data(self, *args, **kwargs):
        context_data = super(IssueDetailView, self).get_context_data(*args, **kwargs)

        if self.object.documentcontent:
            documentcontent = self.object.documentcontent
            if documentcontent.order > 1:
                context_data['tab'] = 'diff'
            else:
                context_data['tab'] = 'view'

            context_data['documentcontent'] = documentcontent
            if self.object.is_processed:
                context_data['selected_diff_documentcontent'] = documentcontent.predecessor
            else:
                context_data['selected_diff_documentcontent'] = documentcontent.document.preferred_version()

        context_data['user_is_member'] = self.object.polity.is_member(self.request.user)
        context_data['can_vote'] = (self.request.user is not None and
                                    self.object.can_vote(self.request.user))
        context_data['comments_closed'] = (
            not self.request.user.is_authenticated() or self.object.discussions_closed()
        )

        return context_data


class IssueOpenListView(ListView):
    model = Issue
    context_object_name = 'newissues'
    template_name = "issue/issues_new.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs['polity'])
        return super(IssueOpenListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        return self.polity.issue_set.order_by('deadline_votes').filter(deadline_votes__gt=datetime.now())

    def get_context_data(self, *args, **kwargs):
        context_data = super(IssueOpenListView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        return context_data
