import json

from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.context_processors import csrf
from django.utils.translation import ugettext_lazy as _
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


@login_required
def issue_add_edit(request, polity_id, issue_id=None, documentcontent_id=None):
    polity = get_object_or_404(Polity, id=polity_id)

    # Make sure that user is allowed to do this.
    if polity.is_newissue_only_officers and request.user not in polity.officers.all():
        raise PermissionDenied()

    if issue_id:
        issue = get_object_or_404(Issue, id=issue_id, polity_id=polity_id)
        current_content = issue.documentcontent

        # We don't want to edit anything that has already been processed.
        if issue.is_processed:
            raise PermissionDenied()
    else:
        issue = Issue(polity=polity)
        if documentcontent_id:
            current_content = get_object_or_404(DocumentContent, id=documentcontent_id)
        else:
            current_content = None

    if request.method == 'POST':
        form = IssueForm(request.POST, instance=issue)
        if form.is_valid():
            issue = form.save(commit=False)
            issue.apply_ruleset()
            issue.documentcontent = current_content
            issue.save()

            issue.topics.clear()
            for topic in request.POST.getlist('topics'):
                issue.topics.add(topic)

            return redirect(reverse('issue', args=(polity_id, issue.id)))
    else:
        # Check if we need to inherit information from previous documentcontent.
        if not issue_id and current_content:
            name = current_content.document.name
            selected_topics = []

            # If this is a new issue, being made from existing content, we
            # want to inherit the previously selected topics, and add a
            # version number to the name.
            if current_content.order > 1:
                name += u', %s %d' % (_(u'version'), current_content.order)
                selected_topics = current_content.previous_topics()

            form = IssueForm(instance=issue, initial={
                'name': name,
                'description': current_content.comments.replace("\n", "\\n"),
                'topics': selected_topics,
            })
        else:
            form = IssueForm(instance=issue)

    # Make only topics from this polity available.
    form.fields['topics'].queryset = Topic.objects.filter(polity=polity)

    ctx = {
        'polity': polity,
        'user_is_member': polity.is_member(request.user),
        'form': form,
        'documentcontent': current_content,
        'tab': 'diff' if current_content.order > 1 else '',
    }

    return render(request, 'issue/issue_form.html', ctx)


def issue_view(request, polity_id, issue_id):
    polity = get_object_or_404(Polity, id=polity_id)
    issue = get_object_or_404(Issue, id=issue_id, polity_id=polity_id)

    ctx = {}

    if issue.documentcontent:
        documentcontent = issue.documentcontent
        if documentcontent.order > 1:
            ctx['tab'] = 'diff'
        else:
            ctx['tab'] = 'view'

        ctx['documentcontent'] = documentcontent
        if issue.is_processed:
            ctx['selected_diff_documentcontent'] = documentcontent.predecessor
        else:
            ctx['selected_diff_documentcontent'] = documentcontent.document.preferred_version()

    ctx['polity'] = polity
    ctx['issue'] = issue
    ctx['user_is_member'] = polity.is_member(request.user)
    ctx['can_vote'] = (request.user is not None and issue.can_vote(request.user))
    ctx['comments_closed'] = not request.user.is_authenticated() or issue.discussions_closed()
    ctx['user_is_officer'] = polity.is_officer(request.user)

    return render(request, 'issue/issue_detail.html', ctx)


def issues_new(request, polity_id):
    polity = get_object_or_404(Polity, id=polity_id)

    newissues = polity.issue_set.order_by('deadline_votes').filter(deadline_votes__gt=datetime.now())

    ctx = {
        'polity': polity,
        'newissues': newissues,
    }
    return render(request, 'issue/issues_new.html', ctx)


@login_required
def document_add(request, polity_id):
    try:
        polity = Polity.objects.get(id=polity_id, members=request.user)
    except Polity.DoesNotExist:
        raise PermissionDenied()

    document = Document(polity=polity, user=request.user)

    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            document.polity = polity
            document.user = request.user
            document.save()
            return redirect('%s?action=new' % reverse('document', args=(polity_id, document.id)))
    else:
        form = DocumentForm()

    ctx = {
        'polity': polity,
        'form': form,
    }
    return render(request, 'issue/document_form.html', ctx)


def document_view(request, polity_id, document_id):
    polity = get_object_or_404(Polity, id=polity_id)
    document = get_object_or_404(Document, id=document_id, polity__id=polity_id)

    # Request variables taken together
    action = request.GET.get('action', '')
    try:
        version_num = int(request.GET.get('v', 0))
    except ValueError:
        raise Exception('Bad "v(ersion)" parameter')

    # If version_num is not specified, we want the "preferred" version
    if version_num > 0:
        current_content = get_object_or_404(DocumentContent, document=document, order=version_num)
    else:
        current_content = document.preferred_version()

    issue = None
    if current_content is not None and hasattr(current_content, 'issue'):
        issue = current_content.issue

    # If current_content is None here, that means the document has no
    # content at all, which is a bit weird unless we're creating a new
    # one...

    ctx = {}

    if action == 'new':
        ctx['editor_enabled'] = True

        current_content = DocumentContent()
        current_content.order = 0
        current_content.predecessor = document.preferred_version()

        if current_content.predecessor:
            current_content.text = current_content.predecessor.text

    elif action == 'edit':
        if current_content.user.id == request.user.id and current_content.status == 'proposed' and issue is None:
            ctx['editor_enabled'] = True


    user_is_member = polity.is_member(request.user)
    user_is_officer = polity.is_officer(request.user)

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
                buttons['put_to_vote'] = 'disabled' if document.has_open_issue() else 'enabled'
            if current_content.user_id == request.user.id:
                buttons['edit_proposal'] = 'disabled' if issue is not None else 'enabled'

    ctx['action'] = action
    ctx['polity'] = polity
    ctx['document'] = document
    ctx['current_content'] = current_content
    ctx['selected_diff_documentcontent'] = document.preferred_version
    ctx['issue'] = issue
    ctx['buttons'] = buttons

    return render(request, 'issue/document_detail.html', ctx)


def document_agreements(request, polity_id):
    polity = get_object_or_404(Polity, id=polity_id)

    user_is_member = polity.is_member(request.user)

    ctx = {
        'polity': polity,
        'agreements': polity.agreements(),
        'user_is_member': user_is_member,
    }
    return render(request, 'issue/document_list.html', ctx)


def document_search(request):
    return render(request, 'issue/search.html')
