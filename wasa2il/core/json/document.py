import markdown2

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from core.models import Document, Issue, ChangeProposal, Statement, DocumentContent
from core.json.utils import jsonize

from google_diff_match_patch.diff_match_patch import diff_match_patch


@login_required
@jsonize
def document_propose_change(request):
    ctx = {"ok": True}
    document = get_object_or_404(Document, id=request.POST.get("document_id", 0))

    try:
        text = request.POST['text']
    except KeyError:
        raise Exception('Missing "text"')

    predecessor = document.preferred_version()
    if predecessor and predecessor.text.strip() == text.strip():
        # This error message won't show anywhere. The same error is caught client-side to produce the error message.
        raise Exception('Change proposal must differ from its predecessor')

    content = DocumentContent()
    content.user = request.user
    content.document = document
    content.text = text
    content.comments = request.POST.get('comments', '')
    content.predecessor = predecessor
    # TODO: Change this to a query that requests the maximum 'order' and adds to it.
    try:
        content.order = DocumentContent.objects.filter(document=document).order_by('-order')[0].order + 1
    except IndexError:
        pass

    content.save()

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
def document_statements_import(request):
    ctx = {}
    ctx["list"] = []

    doc = get_object_or_404(Document, id=request.GET.get("document"))
    text = request.GET.get("text", "")
    lines = text.split("\n")

    if request.user != doc.user:
        return {"error": 403}

    for line in lines:
        s = Statement()
        s.user = request.user
        s.document = doc
        s.text = line[1:].strip()

        if len(line) == 0:
            continue

        if line[0] == "\#":
            # Subheading
            s.type = 3
        elif line[0] == "-":
            # Reference
            s.type = 0
        elif line[0] == ":":
            # Assumption
            s.type = 1
        elif line[0] == "*":
            # Statement
            s.type = 2
        else:
            continue

        try:
            s.number = Statement.objects.get(document=s.document, type=s.type).order_by('-number')[0].number + 1
        except Statement.DoesNotExist:
            s.number = 1
        except IndexError:
            s.number = 1

        s.save()

        boom = {}
        boom["id"] = s.id
        boom["seq"] = s.number
        boom["html"] = str(s)
        ctx["list"].append(boom)

    return ctx


@login_required
@jsonize
def document_statement_new(request, document, type):
    ctx = {}

    doc = get_object_or_404(Document, id=document)

    if doc.is_proposed:
        return document_changeproposal_new(request, document, type)

    s = Statement()
    s.user = request.user
    s.document = doc
    s.type = type
    s.text = request.GET.get('text', '')

    if s.user != s.document.user:
        return {"error": 403}

    try:
        s.number = Statement.objects.get(document=s.document, type=s.type).order_by('-number')[0].number + 1
    except Statement.DoesNotExist:
        s.number = 1
    except IndexError:
        s.number = 1

    s.save()

    ctx["ok"] = True
    ctx["id"] = s.id
    ctx["seq"] = s.number
    ctx["html"] = str(s)

    return ctx


@login_required
@jsonize
def document_statement_move(request, statement, order):
    return {}


@login_required
@jsonize
def document_statement_delete(request, statement):
    return {}


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
    text = request.GET.get('text', 'Missing text!')
    ctx = {}
    ctx['content'] = markdown2.markdown(text, safe_mode='escape')

    return ctx


@jsonize
def documentcontent_render_diff(request):
    ctx = {}

    source_id = request.GET.get('source_id')
    target_id = request.GET.get('target_id')

    target = DocumentContent.objects.get(id=target_id)

    ctx['source_id'] = source_id
    ctx['target_id'] = target_id
    ctx['diff'] = target.diff(source_id)

    return ctx

