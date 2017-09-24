import json

from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.context_processors import csrf
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView


from issue.forms import DocumentForm
from issue.forms import IssueForm
from issue.models import Document
from issue.models import DocumentContent
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


class DocumentCreateView(CreateView):
    model = Document
    context_object_name = "document"
    template_name = "issue/document_form.html"
    form_class = DocumentForm

    def dispatch(self, *args, **kwargs):
        self.polity = None
        if kwargs.has_key('polity'):
            try:
                self.polity = Polity.objects.get(id=kwargs["polity"])
            except Polity.DoesNotExist:
                pass # self.polity defaulted to None already.

        return super(DocumentCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(DocumentCreateView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.polity.is_member(self.request.user)
        return context_data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.polity = self.polity
        self.object.user = self.request.user
        self.object.save()
        self.success_url = "/polity/" + str(self.polity.id) + "/document/" + str(self.object.id) + "/?action=new"
        return HttpResponseRedirect(self.get_success_url())


class DocumentDetailView(DetailView):
    model = Document
    context_object_name = "document"
    template_name = "issue/document_detail.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        return super(DocumentDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        doc = self.object

        context_data = super(DocumentDetailView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})

        # Request variables taken together
        action = self.request.GET.get('action', '')
        try:
            version_num = int(self.request.GET.get('v', 0))
        except ValueError:
            raise Exception('Bad "v(ersion)" parameter')

        # If version_num is not specified, we want the "preferred" version
        if version_num > 0:
            current_content = get_object_or_404(DocumentContent, document=doc, order=version_num)
        else:
            current_content = doc.preferred_version()

        issue = None
        if current_content is not None and hasattr(current_content, 'issue'):
            issue = current_content.issue

        # If current_content is None here, that means the document has no
        # content at all, which is a bit weird unless we're creating a new
        # one...

        if action == 'new':
            context_data['editor_enabled'] = True

            current_content = DocumentContent()
            current_content.order = 0
            current_content.predecessor = doc.preferred_version()

            if current_content.predecessor:
                current_content.text = current_content.predecessor.text

        elif action == 'edit':
            if current_content.user.id == self.request.user.id and current_content.status == 'proposed' and issue is None:
                context_data['editor_enabled'] = True


        user_is_member = self.polity.is_member(self.request.user)
        user_is_officer = self.polity.is_officer(self.request.user)

        buttons = {
            'propose_change': False,
            'put_to_vote': False,
            'edit_proposal': False,
        }
        if ((not issue or not issue.is_voting())
                and current_content is not None):
            if current_content.status == 'accepted':
                if user_is_member:
                    buttons['propose_change'] = 'enabled'
            elif current_content.status == 'proposed':
                if user_is_officer and not issue:
                    buttons['put_to_vote'] = 'disabled' if doc.has_open_issue() else 'enabled'
                if current_content.user_id == self.request.user.id:
                    buttons['edit_proposal'] = 'disabled' if issue is not None else 'enabled'

        context_data['action'] = action
        context_data['current_content'] = current_content
        context_data['selected_diff_documentcontent'] = doc.preferred_version
        context_data['issue'] = issue
        context_data['buttons'] = buttons

        context_data.update(csrf(self.request))
        return context_data


class DocumentListView(ListView):
    model = Document
    context_object_name = "documents"
    template_name = "issue/document_list.html"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        return super(DocumentListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(DocumentListView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data.update({'agreements': [x.preferred_version() for x in context_data["documents"]]})
        context_data['user_is_member'] = self.polity.is_member(self.request.user)
        return context_data

class SearchListView(ListView):
    model = Document
    context_object_name = "documents"
    template_name = "issue/search.html"

    def dispatch(self, *args, **kwargs):
        return super(SearchListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(SearchListView, self).get_context_data(*args, **kwargs)
        return context_data
