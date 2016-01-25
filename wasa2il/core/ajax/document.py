import markdown2

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from core.models import Document, Issue, ChangeProposal, DocumentContent
from core.ajax.utils import jsonize

from google_diff_match_patch.diff_match_patch import diff_match_patch


@login_required
@jsonize
def document_propose_change(request):
    ctx = {"ok": True}
    version_num = int(request.POST.get('v', 0))
    document = get_object_or_404(Document, id=request.POST.get("document_id", 0))

    try:
        text = request.POST['text']
    except KeyError:
        raise Exception('Missing "text"')

    if version_num == 0:
        predecessor = document.preferred_version()
        if predecessor and predecessor.text.strip() == text.strip():
            # This error message won't show anywhere. The same error is caught client-side to produce the error message.
            raise Exception('Change proposal must differ from its predecessor')

        content = DocumentContent()
        content.user = request.user
        content.document = document
        content.predecessor = predecessor
        content.text = text
        content.comments = request.POST.get('comments', '')
        # TODO: Change this to a query that requests the maximum 'order' and adds to it.
        try:
            content.order = DocumentContent.objects.filter(document=document).order_by('-order')[0].order + 1
        except IndexError:
            pass

        content.save()

    else:
        try:
            content = DocumentContent.objects.get(
                document=document,
                user=request.user.id,
                order=version_num,
                status='proposed',
                issue=None
            )
            content.text = text
            content.comments = request.POST.get('comments', '')

            content.save()
        except DocumentContent.DoesNotExist:
            raise Exception('The user "%s" maliciously tried changing document "%s", version %d' % (
                request.user,
                document,
                version_num
            ))

    ctx['order'] = content.order

    return ctx


@login_required
@jsonize
def document_changeproposal_new(request, document, type):
    ctx = {}

    doc = get_object_or_404(Document, id=document)

    if request.user not in doc.polity.members.all():
        ctx['error'] = 403
        return ctx

    s = ChangeProposal()
    s.user = request.user
    s.document = doc
    s.contenttype = type
    s.actiontype = 4
    s.refitem = request.GET.get('after')
    s.destination = request.GET.get('after')  # TODO: Not correct...
    s.content = request.GET.get('text', '')
    s.save()

    return ctx


@login_required
@jsonize
def document_propose(request, document, state):
    ctx = {}

    document = get_object_or_404(Document, id=document)

    if request.user != document.user:
        return {"error": 403}

    ctx["state"] = bool(int(state))
    document.is_proposed = bool(int(state))
    document.save()

    issue_id = int(request.REQUEST.get("issue", 0))
    if issue_id:
        issue = Issue.objects.get(id=issue_id)
        ctx["html_user_documents"] = render_to_string("core/_document_proposals_list_table.html", {"documents": issue.user_documents(request.user)})
        ctx["html_all_documents"] = render_to_string("core/_document_list_table.html", {"documents": issue.proposed_documents()})

    ctx["ok"] = True
    return ctx


@login_required
@jsonize
def render_markdown(request):
    text = request.POST.get('text', 'Missing text!')
    ctx = {}
    ctx['content'] = markdown2.markdown(text, safe_mode='escape')

    return ctx


@jsonize
def documentcontent_render_diff(request):
    ctx = {}

    source_id = request.GET.get('source_id')
    target_id = request.GET.get('target_id')

    target = get_object_or_404(DocumentContent, id=target_id)

    ctx['source_id'] = source_id
    ctx['target_id'] = target_id
    ctx['diff'] = target.diff(source_id)

    return ctx

